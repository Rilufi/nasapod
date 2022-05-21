import tweepy
import os


#calling secret variables
CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]

#connect on twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#search hashtag, RT, like and follow
#three filters: one for only RT the original tweet, other for just media content, safe images and no elon musk
queries = ['#NASA' ,'#space', #cosmology ,'#astronomy', '#hubble']

def rtquery(hash):
    for tweet in tweepy.Cursor(api.search, q=f"{hash} -#elonmusk -@elonmusk -elonmusk -elon -musk -spacex -starlink -tesla -filter:retweets -filter:replies filter:images filter:safe",  result_type="recent").items(1):
        try:
            api.create_friendship(tweet.user.screen_name)
            api.create_favorite(tweet.id)
            tweet.retweet()
            print(f"{hash} rolou.")
        except:
            print(f"{hash} já foi.")
            pass
    
for query in queries:
    rtquery(query)
