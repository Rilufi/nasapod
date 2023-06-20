import tweepy
import os
from auth import api, client
from marstuff import Client

# import keys
api_key = os.environ.get("API_KEY")
client = Client(api_key) 

# Get the latest Photo
photo = client.curiosity.get_latest_photo()
media = api.media_upload(photo)

mystring = ""Latest photo taken by the Curiosity Rover""
client.create_tweet(text=mystring, media_ids=[media.media_id])
