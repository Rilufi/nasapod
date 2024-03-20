# coding=utf-8
import tweepy
import os
import sys
import urllib.request
import requests
from auth import api, client
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import math
from instagrapi import Client
import telebot
import time


# Autentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)

# Get the picture, explanation and/or video thumbnail
URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
      'api_key':api_key,
      'hd':'True',
      'thumbs':'True'
  }
response = requests.get(URL_APOD,params=params).json()
site = (response.get('url'))
thumbs = (response.get('thumbnail_url'))
type = (response.get('media_type'))
explanation = (response.get('explanation'))
title = (response.get('title'))

mystring = f""" Astronomy Picture of the Day

{title}

Source: {site}"""

myexstring = f"""{explanation}"""

### Instagram stuff
##logging instagram
try:
      cl = Client(request_timeout=7)
      cl.login(username, password)
      print('instapod logado')
except:
      print('instapod deslogado')
      bot.send_message(tele_user,  'apod com problema')
      pass

insta_string = f""" Astronomy Picture of the Day
{title}

{explanation}

Source: {site}
#Astronomy #Space #Universe #Astrophotography #Cosmos #Stars #Galaxy #NASA #Science #NightSky"""


### Twitter/X stuff
# Define a function to handle tweet creation with retry and exponential backoff
def create_tweet_with_retry(client, text, media_ids=None):
    max_retries = 5  # Maximum number of retries
    retry_delay = 2  # Initial delay in seconds before the first retry

    for retry_attempt in range(max_retries):
        try:
            # Attempt to create the tweet
            response = client.create_tweet(text=text, media_ids=media_ids)
            if 'id' in response:
                return response['id']  # Return the tweet ID if successful
            else:
                print(f"Error creating tweet: {response}")
                return None
        except Exception as e:
            print(f"Error creating tweet: {e}")
            # Calculate next delay using exponential backoff
            retry_delay *= 2
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying

    print("Max retries exceeded. Unable to create tweet.")
    return None

# Cut the explanation into multiple tweets
def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength  < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end +1
    yield s[start:]

chunks = get_chunks(explanation, 280)

# Make list with line lengths:
chunkex = [(n) for n in chunks]

# Define a list to store tweet IDs
tweet_ids = []

# Post each part of the text and store the tweet IDs
for parte in chunkex:
    # Attempt to create the tweet with retry and exponential backoff
    tweet_id = create_tweet_with_retry(client, str(parte))
    if tweet_id:
        tweet_ids.append(str(tweet_id))

# Check the type of media and post on Twitter and Instagram accordingly
if type == 'image':
    # Post the image on Twitter
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    media = api.media_upload(image)
    tweet_id = create_tweet_with_retry(client, mystring, media_ids=[media.media_id])
    if tweet_id:
        tweet_ids.append(str(tweet_id))
    else:
        print("Failed to create tweet.")

    # Post the image on Instagram
    try:
        cl.photo_upload(image, insta_string)
        print("Photo published on Instagram")
    except Exception as e:
        print(f"Error posting photo on Instagram: {e}")

elif type == 'video':
    # Post the video on Twitter
    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
    video = 'apodvideo.jpeg'
    media = api.media_upload(video)
    tweet_id = create_tweet_with_retry(client, mystring, media_ids=[media.media_id])
    if tweet_id:
        tweet_ids.append(str(tweet_id))
    else:
        print("Failed to create tweet.")

    # Post the video on Instagram
    try:
        cl.video_upload(video, insta_string)
        print("Video published on Instagram")
    except Exception as e:
        print(f"Error posting video on Instagram: {e}")

else:
    print("deu ruim o insta")
    bot.send_message(tele_user,  'apod com problema')

# Concatenate the URLs of the tweets into a threaded tweet
tweet_encadeado = "The official NASA explanation for today's Astronomy Picture of the Day (APOD) can be found in the tweet sequence below: " + "\n".join([f"https://twitter.com/nasobot/status/{tweet_id}" for tweet_id in tweet_ids])

# Publish the threaded tweet
client.create_tweet(text=tweet_encadeado)
