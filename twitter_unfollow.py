import tweepy
from auth import api

class desfollow:

    def unfollower(self):
        followers = api.followers_ids(screen_name=api.me().screen_name)
        print("Followers:", len(followers))
        friends = api.friends_ids(screen_name=api.me().screen_name)
        print("You follow:", len(friends))
        print("The difference between followers and following is:", len(friends)-len(followers))

        while friends > 3000:
            for friend in friends[::-1]:
                if friend not in followers:
                    api.destroy_friendship(friend) 
            friends = api.friends_ids(screen_name=api.me().screen_name)
            print("Now you're following:", len(friends))
