import tweepy
from auth import api
from twitter_unfollow import unfollow

#search hashtag, RT, like and follow
#three filters: one for only RT the original tweet, other for just media content, safe images and no elon musk
queries = ['#NASA' , '#cosmology' ,'#astronomy', '#hubble', '#astrophotography', '#AstroMiniBR', '#AstroThreadBR']

def rtquery(hash):
    for tweet in tweepy.Cursor(api.search, q=f"{hash} -belief -lifeforms -alien -uaptwitter -uap -ufotwitter -quran -metaverse -hubblers -workspace -coverup -flat -flatearther -flatearth -astrology -astrologer -$hbb -OVNI -UFO -@elonmusk -elonmusk -elon -musk -spacex -starlink -tesla -filter:retweets -filter:replies filter:images filter:safe",  result_type="recent").items(1):
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

unfollow = unfollow()
unfollow.unfollow()
