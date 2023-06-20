import tweepy
import os
import sys
import urllib.request
import requests
from auth import api, client

# Autentication
api_key = os.environ["API_KEY"]

# Get the picture, explanation and/or video thumbnail
URL_APOD = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/latest_photos"
params = {
      'api_key':api_key,
  }
response = requests.get(URL_APOD, params=params).json()
latest_photos = response.get('latest_photos')
latest_photo = latest_photos[0]

camera = latest_photo['camera']['full_name']
sol = latest_photo['sol']
site = latest_photo['img_src']

mystring = f""" Latest Curiosity Rover Picture

Taken from the {camera} on Sol {sol}

Source: {site}"""

print(mystring)
urllib.request.urlretrieve(site, 'rovertoday.jpeg')
image = "rovertoday.jpeg"
media = api.media_upload(image)
client.create_tweet(text=mystring, media_ids=[media.media_id])
