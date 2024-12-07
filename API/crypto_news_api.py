import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import pandas as pd
import os
from API.scrape_details import scrape_url
from API.tokens import *
from transformers import pipeline # type: ignore
import math
import sys
from transformers import AutoTokenizer # type: ignore
from torch.nn.functional import softmax
import torch
from transformers import pipeline

# Specify device: 0 for GPU, -1 for CPU


# Load FinBERT tokenizer


# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "job",
    "host": "localhost",  # Replace with your database host if needed
    "port": 5432,         # Default PostgreSQL port
}

# Function to create the articles table
def create_articles_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS crypto_news.articles_latest (
        id SERIAL PRIMARY KEY,
        news_url TEXT NOT NULL,
        image_url TEXT,
        title TEXT NOT NULL,
        text TEXT,
        source_name TEXT,
        date TIMESTAMP,
        sentiment TEXT,
        sentiment_score NUMERIC,
        topics TEXT[],
        type TEXT,
        tickers TEXT[],
        full_text TEXT,
        full_text_sentiment_positive NUMERIC,
        full_text_sentiment_negative NUMERIC,
        full_text_sentiment_neutral NUMERIC
    );
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_query)
                conn.commit()
                print("Table 'articles' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

def chunk_large_text(text, tokenizer, max_length=512):
    """
    Splits a large text into smaller chunks that fit the model's maximum token limit.

    Args:
        text (str): The input text to chunk.
        tokenizer: The tokenizer used for tokenizing the text.
        max_length (int): The maximum token length allowed by the model.

    Returns:
        List[str]: A list of text chunks.
    """
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_length):
        chunk = tokenizer.convert_tokens_to_string(tokens[i:i + max_length])
        chunks.append(chunk)
    return chunks



import torch
from torch.nn.functional import softmax

def analyze_large_text_sentiment(text, tokenizer, model):
    """
    Analyzes sentiment for a large text by processing it in smaller chunks.

    Args:
        text (str): The input large text.
        tokenizer: The tokenizer used for tokenizing the text.
        model: The sentiment analysis model.

    Returns:
        dict: Aggregated sentiment scores (positive, neutral, negative).
    """
    # Chunk the text
    chunks = chunk_large_text(text, tokenizer, max_length=512)

    # Initialize sentiment probabilities
    sentiment_totals = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}

    # Process each chunk
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True, max_length=512)

        # Move tensors to GPU if available
        if torch.cuda.is_available():
            inputs = {key: value.cuda() for key, value in inputs.items()}
            model = model.cuda()

        with torch.no_grad():
            outputs = model(**inputs)

        # Extract probabilities
        logits = outputs.logits
        probs = softmax(logits, dim=-1)[0].tolist()

        # Aggregate sentiment probabilities
        sentiment_totals["negative"] += probs[0]
        sentiment_totals["neutral"] += probs[1]
        sentiment_totals["positive"] += probs[2]

    # Average the probabilities over all chunks
    num_chunks = len(chunks) or 1
    aggregated_scores = {label: score / num_chunks for label, score in sentiment_totals.items()}

    return aggregated_scores






# Function to fetch all news for a given ticker
def fetch_all_news(api_key, ticker, start_date, end_date , finbert,  tokenizer):
    base_url = "https://cryptonews-api.com/api/v1"
    all_articles = []
    page = 1
    items = 100  # Maximum allowed by the API

    while True:
        url = (f"{base_url}?tickers={ticker}&items={items}&page={page}"
               f"&start_date={start_date}&end_date={end_date}&token={api_key}")
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"API call failed: {response.text}")

        data = response.json().get("data", [])
        if not data:  # No more articles
            break
        for item in data:
            item['full_text'] = scrape_url(item['news_url'])

            item['full_text_sentiment_positive']  ,  item['full_text_sentiment_neutral'] ,  item['full_text_sentiment_negative'] = analyze_large_text_sentiment(item['full_text'] , tokenizer , model = finbert).values()
            all_articles.append(item)
            # ingest_articles_to_db(item)
        page += 1

    return all_articles

# Function to parse the date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Function to ingest articles into the database
def ingest_articles_to_db(articles):
    insert_query = """
    INSERT INTO crypto_news.articles_latest (
        news_url, image_url, title, text, source_name, date, sentiment, sentiment_score, topics, type, tickers, full_text , full_text_sentiment_positive , full_text_sentiment_negative ,  full_text_sentiment_neutral
        ) VALUES %s
    """
    values = [
        (
            article.get("news_url"),
            article.get("image_url"),
            article.get("title"),
            article.get("text"),
            article.get("source_name"),
            parse_date(article.get("date")),
            article.get("sentiment"),
            article.get("sentiment_score"),
            article.get("topics"),
            article.get("type"),
            article.get("tickers"),
            article.get("full_text"),
            article.get("full_text_sentiment_positive"),
            article.get("full_text_sentiment_negative"),
            article.get("full_text_sentiment_neutral")
        )
        for article in articles
    ]

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                execute_values(cur, insert_query, values)
                conn.commit()
                print(f"{len(articles)} articles ingested successfully.")
    except Exception as e:
        print(f"Error ingesting articles: {e}")

# Main script
if __name__ == "__main__":
    api_key = api_key # Replace with your API key
    csv_files = os.listdir('data/')  # Replace with your CSV files
    finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone" , tokenizer = "yiyanghkust/finbert-tone" , device = 0)
    create_articles_table()  # Create the articles table if not exists

    for csv_file in csv_files:
        if( csv_file.split("-")[0] in ["BTC", "ETH", "BNB", "USDT", "ADA", "XRP", "USDC", "DOGE", "SOL", "DOT"]):
            # Extract ticker and date range from CSV
            df = pd.read_csv("data/"+csv_file, parse_dates=["Datetime"])
            start_date = df["Datetime"].min().strftime("%Y-%m-%d")
            end_date = df["Datetime"].max().strftime("%Y-%m-%d")
            ticker = csv_file.split("-")[0]  # Assuming file name is <TICKER>.csv

            print(f"Fetching articles for {ticker} from {start_date} to {end_date}...")
            articles = fetch_all_news(api_key, ticker, start_date, end_date , finbert , tokenizer = None)

        # Ingest articles into the database
        # ingest_articles_to_db(articles)
