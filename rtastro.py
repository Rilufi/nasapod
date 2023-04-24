import tweepy
from auth import api

#search hashtag, RT, like and follow
#four filters: only RT the original tweet, media content, safe images and no elon musk

queries = ['#NASA' , '#cosmology' ,'#astronomy', '#hubble', '#astrophotography', '#AstroMiniBR', '#AstroThreadBR']

def rtquery(hash):
    for tweet in tweepy.Cursor(api.search, q=f"{hash} -God -Jesus -metta -RoboticDogs -RBIF -positivethinking -goodvibes -healing -belief -lifeforms -alien -uaptwitter -uap -ufotwitter -quran -metaverse -hubblers -workspace -coverup -flat -flatearther -flatearth -astrology -astrologer -$hbb -OVNI -UFO -@elonmusk -elonmusk -elon -musk -spacex -starlink -tesla -filter:retweets -filter:replies filter:images filter:safe",  result_type="recent").items(1):
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
