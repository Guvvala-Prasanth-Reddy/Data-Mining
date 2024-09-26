import tweepy

# Replace these with your actual Twitter API credentials
BEARER_TOKEN = 'your_bearer_token'

# Setup Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Define the cryptocurrency query
query = "Bitcoin -is:retweet"  # Fetch tweets containing 'Bitcoin' excluding retweets

# Fetch tweets (max_results can be set up to 100)
tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=["created_at", "text"])

# Print the tweets
for tweet in tweets.data:
    print(f"Time: {tweet.created_at}, Tweet: {tweet.text}")
