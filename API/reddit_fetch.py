from tokens import *
import praw

def check_and_return_connection():

    reddit = praw.Reddit(client_id= client_id,
                     client_secret=secret_id,
                     user_agent=user_agent)

    print("Authenticated:", reddit.read_only)
    return reddit
def fetch_posts( subreddit , crypto_title):
    bitcoin_posts = []
    for post in subreddit.search(crypto_title, limit=100):
        bitcoin_posts.append({
            'title': post.title,
            'url': post.url,
            'score': post.score,
            'comments': post.num_comments,
            'body': post.selftext
        })

    # Display some Bitcoin-related posts
    for idx, post in enumerate(bitcoin_posts[:5]):
        print(f"Bitcoin Post {idx+1}:")
        print(f"Title: {post['title']}")
        print(f"Score: {post['score']}, Comments: {post['comments']}")
        print(f"URL: {post['url']}\n")
        print(f"BODY:{post['body']}\n")
    return bitcoin_posts
if __name__ =='__main__':
    reddit = check_and_return_connection()
    subreddit = reddit.subreddit('cryptocurrency')
    posts = fetch_posts( subreddit=subreddit , crypto_title='BitCoin')
