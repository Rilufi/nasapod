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


# Autentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

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
media = (response.get('media_type'))
explanation = (response.get('explanation'))
title = (response.get('title'))

mystring = f""" Astronomy Picture of the Day

{title}

Source: {site}"""

# Decide whether is an image or a video and post

if media == 'image':
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    media = api.media_upload(image)
    client.create_tweet(text=mystring, media_ids=[media.media_id])
    #api.update_with_media(image, mystring)
elif media == 'video':
    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
    video = 'apodvideo.jpeg'
    media = api.media_upload(video)
    client.create_tweet(text=mystring, media_ids=[media.media_id])    
    #api.update_with_media(video, mystring)
else:
    client.create_tweet(text = mystring)


##logging instagram
try:
  cl = Client(request_timeout=7)
  cl.login(USERNAME, PASSWORD)
  print('instapod logado')
except:
  print('instapod deslogado')
  pass


insta_string = f""" Astronomy Picture of the Day - {title}

{explanation}

Source: {site}"""

if media == 'image':
      cl.photo_upload(image, insta_string)
elif media == 'video':
      cl.photo_upload(video, insta_string)
else:
      print("deu ruim o insta")
      pass
