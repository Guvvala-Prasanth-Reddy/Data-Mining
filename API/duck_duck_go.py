import pandas as pd
import numpy as np
from DB import store
from ratelimit import limits, sleep_and_retry
from API.exponential_backoff import exponential_backoff
ONE_SECOND = 1
# Generate a date range from January 1, 2023 to January 10, 2023
from duckduckgo_search import DDGS # type: ignore
from API.scrape_details import scrape_url
import time
from datetime import datetime
from urllib.parse import urlparse

@sleep_and_retry
@limits(calls=20, period=ONE_SECOND)
@exponential_backoff(retries=10 , backoff_factor=2)
def search_duckduckgo_news(query, max_results=10):
    with DDGS() as ddgs:
        results = ddgs.news(query, max_results=max_results)
        links = [result['url'] for result in results]
    return links

# Example usage
def store_data_incremental_load(ticker , max_results):
    query = f"{ticker} crypto sensational news today"
    try:
        news_links = search_duckduckgo_news(query, max_results=max_results)
    except Exception as e:
        print(f'failed to fetch news for {ticker} : {e}')
        return 
    
    for idx, link in enumerate(news_links, 1):
        print(f"{idx}. {link}")
        try:
            content = scrape_url(link)
            print( content , type(content))
            article_data = {
            "crypto_name": f"{ticker}",
            "content": f"{content}",
            "source": f"{urlparse(link).netloc}",
            "insertion_date": datetime.today(),
            "url": f"{link}",
            "sentiment_score": 0
        }
            store.insert_article( **article_data)
        except Exception as e:
            print(f"Failed to process link {link}: {e}")

if __name__ == '__main__':
    tickers = np.load('crypto_tickers.npy')
    tickers_real = []
    for i in tickers:
        tickers_real.append( i.split('-')[0])
    print(tickers_real)
    for tick in tickers_real:
        store_data_incremental_load( ticker=tick ,  max_results=10)