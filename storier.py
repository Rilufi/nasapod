import os
from instagrapi import Client
from instagrapi.exceptions import ClientError
import time

# Authentication
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Initialize the client
client = Client()
client.login(username, password)  # Log in to your account

# ID of NASA's official Instagram account
nasa_user_id = "1518284433"  # ID of NASA's official account

# Get followers of NASA's official account
try:
    followers = client.user_followers(nasa_user_id, amount=50)  # Get 50 followers of NASA
    for follower in followers:
        # Check if the follower object is a string (username) or a dictionary (follower)
        if isinstance(follower, str):
            user_info = client.user_info_by_username(follower)
            client.user_follow(user_info.pk)
            print(f"Following {user_info.username}")
        else:
            client.user_follow(follower["pk"])
            print(f"Following {follower['username']}")
        time.sleep(360)  # Wait 6 minutes before following the next follower (50 followers in 5 hours)
except ClientError as e:
    print(f"Error getting NASA's followers: {e}")

# Logout
client.logout()
