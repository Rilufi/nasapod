import tweepy
from auth import api
import sys

class desfollow:

    def unfollower(self):
        followers = api.followers_ids(screen_name=api.me().screen_name)
        friends = api.friends_ids(screen_name=api.me().screen_name)
        print("You follow:", len(friends))
        
        for friend in friends[::-1]:
            if friend not in followers:
                if len(friends) > 3000:
                    api.destroy_friendship(friend) 
                else:
                    friends = api.friends_ids(screen_name=api.me().screen_name)
                    print("Now you're following:", len(friends))
                    sys.exit()
