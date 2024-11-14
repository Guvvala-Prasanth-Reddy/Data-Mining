from tokens import *
import praw
from scrape_details import scrape_url
import requests
from datetime import datetime , timedelta
from api_key import *
import os
from bs4 import BeautifulSoup

def check_and_return_connection():

    reddit = praw.Reddit(client_id= client_id,
                     client_secret=secret_id,
                     user_agent=user_agent)

    print("Authenticated:", reddit.read_only)
    return reddit


def fetch_posts_search_api( query , num_results):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    search_url = f"https://html.duckduckgo.com/html?q={query}&t=news"

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve results: Status code {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    
    for result in soup.find_all('a', class_='result__a', limit=num_results):
        links.append(result['href'])


# Example usage

    # bitcoin_posts = []
    # post_title = {}
    # specific_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # start_timestamp = int(specific_date.timestamp())
    # end_timestamp = int((specific_date + timedelta(days=1)).timestamp())
    
    # after_timestamp = end_timestamp  # Start fetching posts before the end of today

    # while len(bitcoin_posts) < 100:
    #     # Fetch posts in batches of 100, filtering only today's posts
    #     for post in subreddit.search(crypto_title, limit=100, params={'before': after_timestamp}):
    #         # Only include posts within the specified date range
    #         if start_timestamp <= post.created_utc < end_timestamp and post.title not in post_title:
    #             bitcoin_posts.append({
    #                 'title': post.title,
    #                 'url': post.url,
    #                 'score': post.score,
    #                 'comments': post.num_comments,
    #                 'body': scrape_url(post.url),
    #             })
    #             post_title[post.title] = True
    #             after_timestamp = post.created_utc  # Update to fetch earlier posts

    #         # Stop if we have collected 100 posts
    #         if len(bitcoin_posts) >= 10:
    #             break
    #         print(len(bitcoin_posts))

    #     # Stop if there are no more posts available
    #     if not bitcoin_posts:
    #         print("No more posts found for today.")
    #         break

    # print(f"Fetched {len(bitcoin_posts)} posts from today.")
    # return bitcoin_posts

    # bitcoin_posts = []
    # for post in subreddit.search(crypto_title, limit=100):
    #     bitcoin_posts.append({
    #         'title': post.title,
    #         'url': post.url,
    #         'score': post.score,
    #         'comments': post.num_comments,
    #         'body': scrape_url(post.url),
    #     })
    #     # text = 
    # print(len(bitcoin_posts))

    # # Display some Bitcoin-related posts
    # for idx, post in enumerate(bitcoin_posts[:5]):
    #     print(f"Bitcoin Post {idx+1}:")
    #     print(f"Title: {post['title']}")
    #     print(f"Score: {post['score']}, Comments: {post['comments']}")
    #     print(f"URL: {post['url']}\n")
    #     print(f"BODY : {post['body']}\n")
    # return bitcoin_posts
if __name__ =='__main__':
    # reddit = check_and_return_connection()
    # subreddit = reddit.subreddit('cryptocurrency')
    specific_date =  datetime.today()
    # posts = fetch_posts(  crypto_title='BTC' , specific_date=specific_date)
    query = "btc news today"
    news_links = fetch_posts_search_api(query, num_results=5)
    for idx, link in enumerate(news_links, 1):
        print(f"{idx}. {link}")

    # print(len(posts))