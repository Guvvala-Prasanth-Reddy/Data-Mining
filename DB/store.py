from pymongo import MongoClient # type: ignore
from datetime import datetime
from DB.credentials import *

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Function to insert an article
def insert_article(crypto_name,  content, source, insertion_date, url, sentiment_score=None):
    # Check if the article already exists based on URL
    if not collection.find_one({"url": url}):
        article = {
            "crypto_name": crypto_name,
            "content": content,
            "source": source,
            "insertion_date": insertion_date,
            "url": url,
            "sentiment_score": sentiment_score,
            "created_at": datetime.now()
        }
        collection.insert_one(article)
        print(f"Article added: {url}")
    else:
        print(f"Article already exists: {url}")

# Function to fetch articles by cryptocurrency
def fetch_articles_by_crypto(crypto_name):
    return list(collection.find({"crypto_name": crypto_name}))

# Function to fetch all articles
def fetch_all_articles():
    return list(collection.find())

# Function to delete articles for a specific cryptocurrency
def delete_articles_by_crypto(crypto_name):
    result = collection.delete_many({"crypto_name": crypto_name})
    print(f"Deleted {result.deleted_count} articles for {crypto_name}.")

# Example usage
if __name__ == "__main__":
    # Example article data
    article_data = {
        "crypto_name": "Bitcoin",
        "title": "Bitcoin hits $70,000",
        "content": "Bitcoin reaches an all-time high...",
        "source": "Crypto News",
        "publication_date": datetime(2024, 11, 16, 10, 30),
        "url": "https://example.com/bitcoin-70000",
        "sentiment_score": 0.95
    }
    
    # Insert an article
    insert_article(**article_data)
    
    # Fetch and print all articles for Bitcoin
    bitcoin_articles = fetch_articles_by_crypto("Bitcoin")
    print(f"Articles for Bitcoin: {bitcoin_articles}")
    
    # Fetch and print all articles
    all_articles = fetch_all_articles()
    print(f"All Articles: {all_articles}")

    # Delete articles for Bitcoin
    delete_articles_by_crypto("Bitcoin")
