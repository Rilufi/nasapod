import tweepy
from auth import api

class unfollow:
    def unfollow(self):
        my_screen_name = api.me().screen_name
        user = api.get_user(screen_name=my_screen_name)
        print('\n--------------------')
        print(user.name)
        print('--------------------')
        print(my_screen_name + ' has ' + str(user.friends_count) + ' friends')
        if user.friends_count > 3000:
            inactive_friends = [];
            friends = api.friends_ids(screen_name=my_screen_name)
            for friend in friends[::-1]:
                tweets_list= api.user_timeline(user_id = friend, exclude_replies = 'true', include_rts = 'false', count = 1)
                try:
                    tweet = tweets_list[0]
                    delta = date.today() - tweet.created_at.date()
                    if (len(inactive_friends) >= user.friends_count - 3000):
                        break
                    elif (delta.days < 30):
                        continue
                    else:
                        inactive_friends.append(friend)
                except:
                    pass
            if (len(inactive_friends) > 0):
                print('Unfollowing %s friends..' % len(inactive_friends))
                for friend in inactive_friends:
                    api.destroy_friendship(friend)
        elif user.friends_count <= 3000:
            print(f"sem unfollow p/ {my_screen_name} hoje")
        else:
            print(f"tentei p/ {my_screen_name}, mas não rolou.")
