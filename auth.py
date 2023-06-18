import tweepy
import os

client = tweepy.Client(
    consumer_key = os.environ.get("CONSUMER_KEY"),
    consumer_secret = os.environ.get("CONSUMER_SECRET"),
    access_token = os.environ.get("ACCESS_TOKEN"),
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
)

#calling secret variables
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

#connect on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
