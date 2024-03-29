# coding=utf-8
import os
import urllib.request
import requests
import tweepy
import time
from auth import api, client
from instagrapi import Client
import telebot


# Authentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)


# Get the picture, explanation, and/or video thumbnail
URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
      'api_key':api_key,
      'hd':'True',
      'thumbs':'True'
  }
response = requests.get(URL_APOD, params=params).json()
site = response.get('url')
thumbs = response.get('thumbnail_url')
type = response.get('media_type')
explanation = response.get('explanation')
title = response.get('title')
hashtags = "#NASA #APOD #Astronomy #Space #Astrophotography"

mystring = f"""Astronomy Picture of the Day

{title}

Source: {site}

{hashtags}"""

insta_string = f""" Astronomy Picture of the Day
{title}

{explanation}

Source: {site}

{hashtags}"""

myexstring = f"""{explanation}"""

# Cut the explanation into multiple tweets
def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

chunks = get_chunks(explanation, 280)


# Check the type of media and post on Twitter and Instagram accordingly
if type == 'image':
    # Post the image on Twitter
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    media = api.media_upload(image)
    tweet_imagem = client.create_tweet(text=mystring, media_ids=[media.media_id])
    # Salva o ID do tweet da imagem
    tweet_id_imagem = tweet_imagem.data['id']

    # Post the image on Instagram
    try:
        cl = Client(request_timeout=7)
        cl.login(username, password)
        cl.photo_upload(image, insta_string)
        print("Photo published on Instagram")
    except Exception as e:
        print(f"Error posting photo on Instagram: {e}")

elif type == 'video':
    # Post the video on Twitter
    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
    video = 'apodvideo.jpeg'
    media = api.media_upload(video)
    tweet_imagem = client.create_tweet(text=mystring, media_ids=[media.media_id])
    # Salva o ID do tweet da imagem
    tweet_id_imagem = tweet_imagem.data['id']

    # Post the video on Instagram
    try:
        cl = Client(request_timeout=7)
        cl.login(username, password)
        cl.video_upload(video, insta_string)
        print("Video published on Instagram")
    except Exception as e:
        print(f"Error posting video on Instagram: {e}")

else:
    print("Something went wrong with the media type.")
    bot.send_message(tele_user, 'apod com problema')

# Post each part of the explanation as a reply to the previous tweet
tweet_ids_explicacao = []
reply_to_id = tweet_id_imagem  # Start by replying to the tweet with the image and title

for parte in chunks:
    try:
        response = client.create_tweet(text=str(parte), in_reply_to_tweet_id=reply_to_id)
        if 'id' in response.data:
            tweet_ids_explicacao.append(str(response.data['id']))
            reply_to_id = response.data['id']  # Update the ID for the next reply
        else:
            print(f"Error creating tweet: {response.data}")
    except Exception as e:
        print(f"Error creating tweet: {e}")
