import tweepy
import os
import sys
import urllib.request
import requests
from auth import api, client
import datetime


today = datetime.date.today()
hoje = today.strftime('%Y-%m-%d')
api_key = os.environ["API_KEY"]
#api_key = "DEMO_KEY"

def rover_pic(URL_APOD, rover_name):
    # Get the picture after specifying the rover
    params = {
          'api_key':api_key,
      }
    response = requests.get(URL_APOD, params=params).json()
    rover = response.get('rover')
    max_date = rover['max_date']
    if max_date == hoje:
        URL_APOD = URL_APOD+'latest_photos'
        response = requests.get(URL_APOD, params=params).json()
        latest_photos = response.get('latest_photos')
        latest_photo = latest_photos[0]
        camera = latest_photo['camera']['full_name']
        sol = latest_photo['sol']
        site = latest_photo['img_src']

        mystring = f""" Latest {rover_name} Rover Picture

Taken from the {camera} on Sol {sol}

Source: {site}"""

        urllib.request.urlretrieve(site, 'rovertoday.jpeg')
        image = "rovertoday.jpeg"
        media = api.media_upload(image)
        client.create_tweet(text=mystring, media_ids=[media.media_id])
        print(mystring)
    else:
        print(f'Sem {rover_name} hoje')
        pass

rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/", 'Curiosity')
rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/", 'Perseverance')
rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/spirit/", 'Spirit')
