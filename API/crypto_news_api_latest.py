import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import pandas as pd
import os
from API.scrape_details import scrape_url
from API.tokens import *
from transformers import pipeline
import torch
from transformers import AutoTokenizer, pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "job",
    "host": "localhost",
    "port": 5432,
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
def sliding_window_tokenizer(text, tokenizer, max_length=512, stride=256):
    """
    Tokenizes a long text using a sliding window approach to generate overlapping chunks.

    Args:
        text (str): Input text to tokenize.
        tokenizer: The tokenizer for the FinBERT model.
        max_length (int): Maximum token length (default: 512).
        stride (int): Overlap size for sliding window chunks (default: 256).

    Returns:
        Dict[str, torch.Tensor]: Tokenized chunks with input IDs, attention masks, etc.
    """
    inputs = tokenizer(
        text,
        add_special_tokens=True,
        return_tensors="pt",
        max_length=max_length,
        stride=stride,
        truncation=True,
        padding="max_length",
        return_overflowing_tokens=True,
        return_offsets_mapping=True,  # Useful for debugging offsets
    )
    return inputs




def analyze_sentiment_long_text(text, tokenizer, model, max_length=512, stride=256):
    """
    Analyzes sentiment for a large text using the sliding window approach.

    Args:
        text (str): The input text.
        tokenizer: The tokenizer for the FinBERT model.
        model: The FinBERT model.
        max_length (int): Maximum token length for each chunk (default: 512).
        stride (int): Overlap size for sliding window chunks (default: 256).

    Returns:
        dict: Aggregated sentiment scores (positive, neutral, negative).
    """
    # Tokenize using sliding window
    tokenized_inputs = sliding_window_tokenizer(text, tokenizer, max_length, stride)

    sentiment_totals = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    num_chunks = len(tokenized_inputs["input_ids"])

    for i in range(num_chunks):
        # Extract the input IDs and attention mask for each chunk
        input_ids = tokenized_inputs["input_ids"][i].unsqueeze(0).to(model.device)
        attention_mask = tokenized_inputs["attention_mask"][i].unsqueeze(0).to(model.device)

        # Pass inputs through the model
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)

        # Aggregate sentiment scores
        sentiment_totals["negative"] += probs[0][0].item()
        sentiment_totals["neutral"] += probs[0][1].item()
        sentiment_totals["positive"] += probs[0][2].item()

    # Normalize scores across all chunks
    aggregated_scores = {label: score / num_chunks for label, score in sentiment_totals.items()}
    return aggregated_scores


def fetch_all_news(api_key, ticker, start_date, end_date, model, tokenizer):
    base_url = "https://cryptonews-api.com/api/v1"
    all_articles = []
    page = 1
    items = 100

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
            item['full_text'] = scrape_url(item['news_url']) or ""
            if item['full_text']:
                sentiments = analyze_sentiment_long_text(item['full_text'], tokenizer , model)
                item['full_text_sentiment_positive'] = sentiments['positive']
                item['full_text_sentiment_negative'] = sentiments['negative']
                item['full_text_sentiment_neutral'] = sentiments['neutral']
            all_articles.append(item)

        page += 1

    return all_articles







# Function to parse the date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Function to ingest articles into the database
def ingest_articles_to_db(articles):
    insert_query = """
    INSERT INTO crypto_news.articles_latest (
        news_url, image_url, title, text, source_name, date, sentiment, sentiment_score,
        topics, type, tickers, full_text, full_text_sentiment_positive, full_text_sentiment_negative,
        full_text_sentiment_neutral
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
            article.get("full_text_sentiment_neutral"),
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
    api_key = api_key  # Replace with your API key
    csv_files = os.listdir("data/")  # Replace with your CSV files
    # finbert_model = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone", device=0)
    # finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone") 
    # Load FinBERT tokenizer and model
    finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    finbert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
    finbert_model = finbert_model.to("cuda" if torch.cuda.is_available() else "cpu")

    create_articles_table()  # Create the articles table if not exists

    for csv_file in csv_files:
        if csv_file.split("-")[0] in ["BTC", "ETH", "BNB", "USDT", "ADA", "XRP", "USDC", "DOGE", "SOL", "DOT"]:
            df = pd.read_csv("data/" + csv_file, parse_dates=["Datetime"])
            start_date = df["Datetime"].min().strftime("%Y-%m-%d")
            end_date = df["Datetime"].max().strftime("%Y-%m-%d")
            ticker = csv_file.split("-")[0]

            print(f"Fetching articles for {ticker} from {start_date} to {end_date}...")
            articles = fetch_all_news(api_key, ticker, start_date, end_date, finbert_model , finbert_tokenizer)
            ingest_articles_to_db(articles)
