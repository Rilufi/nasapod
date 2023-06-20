import tweepy
import os
import sys
import urllib.request
import requests
from auth import api, client

# Autentication
api_key = os.environ["API_KEY"]

def rover_pic(URL_APOD, rover):
    # Get the picture after specifying the rover
    params = {'api_key':api_key}
    response = requests.get(URL_APOD, params=params).json()
    latest_photos = response.get('latest_photos')
    latest_photo = latest_photos[0]
    camera = latest_photo['camera']['full_name']
    sol = latest_photo['sol']
    site = latest_photo['img_src']

    mystring = f""" Latest Mars Picture from the {rover}

Taken from the {camera} on Sol {sol}

Source: {site}"""

    urllib.request.urlretrieve(site, 'rovertoday.jpeg')
    image = "rovertoday.jpeg"
    media = api.media_upload(image)
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    print(mystring)

try:
    rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/latest_photos", 'Curiosity')
except:
    print('Curiosity já foi.')
try:
    rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/latest_photos", 'Perseverance')
except:
    print('Perseverance já foi.')
try:
    rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/spirit/latest_photos", 'Spirit')
except:
    print('Spirit já foi.')
