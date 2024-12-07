import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "crypto_news",
    "user": "postgres",
    "password": "job",
    "host": "localhost",  # Replace with your database host if needed
    "port": 5432,         # Default PostgreSQL port
}

# Create the articles table
def create_articles_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS articles (
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
        tickers TEXT[]
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

# Function to parse the date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Ingest articles into the table
def ingest_articles(articles):
    insert_query = """
    INSERT INTO articles (
        news_url, image_url, title, text, source_name, date, sentiment, sentiment_score, topics, type, tickers
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

# Example usage
if __name__ == "__main__":
    create_articles_table()

    # Example articles data
    articles = [
        {
            "news_url": "https://thenewscrypto.com/el-salvador-reaps-rewards-as-bitcoin-breaks-100k/?utm_source=snapi",
            "image_url": "https://crypto.snapi.dev/images/v1/l/f/w/btc2-571822-607073.jpg",
            "title": "El Salvador Reaps Rewards as Bitcoin Breaks $100K",
            "text": "Bitcoin's $100K milestone strengthens El Salvador's financial position and debt refinancing. Market shows bullish demand, but technical indicators suggest potential for sell-off.",
            "source_name": "TheNewsCrypto",
            "date": "Fri, 06 Dec 2024 12:00:41 -0500",
            "sentiment": "Positive",
            "sentiment_score": 0.95,
            "topics": ["pricemovement"],
            "type": "Article",
            "tickers": ["BTC"],
        }
    ]

    # Ingest example articles
    ingest_articles(articles)
