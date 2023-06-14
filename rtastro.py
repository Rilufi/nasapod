import tweepy
from auth import api
import random

#search hashtag, RT, like and follow
#four filters: only RT the original tweet, media content, safe images and no elon musk

queries = ['#NASA' , '#cosmology' ,'#astronomy', '#hubble', '#astrophotography', '#AstroMiniBR', '#AstroThreadBR']

def rtquery(hash):
#    for tweet in tweepy.Cursor(api.search, q=f"{hash} -God -Jesus -metta -RoboticDogs -RBIF -positivethinking -goodvibes -healing -belief -lifeforms -alien -uaptwitter -uap -ufotwitter -quran -metaverse -hubblers -workspace -coverup -flat -flatearther -flatearth -astrology -astrologer -$hbb -OVNI -UFO -@elonmusk -elonmusk -elon -musk -spacex -starlink -tesla -filter:retweets -filter:replies filter:images filter:safe",  result_type="recent").items(1):
    tweet = api.search_recent_tweets(f"{hash} -God -Jesus -metta -RoboticDogs -RBIF -positivethinking -goodvibes -healing -belief -lifeforms -alien -uaptwitter -uap -ufotwitter -quran -metaverse -hubblers -workspace -coverup -flat -flatearther -flatearth -astrology -astrologer -$hbb -OVNI -UFO -@elonmusk -elonmusk -elon -musk -spacex -starlink -tesla -filter:retweets -filter:replies filter:images filter:safe", max_results=1)#.items(1):
    try:
        api.create_friendship(tweet.user.screen_name)
        api.like(tweet.id)
        tweet.retweet()
        print(f"{hash} rolou.")
    except:
        print(f"{hash} já foi.")
        pass

for query in queries:
    rtquery(query)


lines=open('lista_links.txt').read().splitlines()
status = random.choice(lines)+'/?ref=gedp4al8'
mystring = f""" Calling all stargazers! Explore the universe with captivating astronomy-themed merchandise from The Space Store. Discover celestial treasures and ignite your passion for the cosmos. Start your cosmic shopping journey today! ✨🌌 #Astronomy
{status}"""

try:
    api.create_tweet(text = mystring)
except:
    pass
