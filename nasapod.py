# coding=utf-8

import tweepy
import os
import sys
from nasa import apod
import urllib.request
import requests

# Autentication

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

os.environ['NASA_API_KEY'] = ''
api_key = ''

# Get the picture/explanation

picture = apod.apod()
site = str(picture.url)
explanation = str(picture.explanation)

toReply = "" # user to get most recent tweet

site = picture.url
title = picture.title

# Get the video thumbnail

URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
      'api_key':api_key,
      'hd':'True',
      'thumbs':'True'
  }
response = requests.get(URL_APOD,params=params).json()
thumbs = (response.get('thumbnail_url'))
type = (response.get('media_type'))


mystring = f""" Astronomy Picture of the Day

{title}

Fonte: {site}"""

# Decide whether is an image or a video and post

if type == 'image':
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    api.update_with_media(image, mystring)
elif type == 'video':
    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
    video = 'apodvideo.jpeg'
    api.update_with_media(video, mystring)
else:
    api.update_status(mystring)

myexstring = f"""{explanation}"""

# Cut the explanation into multiple tweets

def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength  < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end +1
    yield s[start:]

chunks = get_chunks(myexstring, 280)

# Make list with line lengths:
chunkex = [(n) for n in chunks]

coun = 0

# Post the explanation

while coun < len(chunkex):
    tweets = api.user_timeline(screen_name = toReply, count=1)
    for tweet in tweets:
        api.update_status(str(chunkex[coun]), in_reply_to_status_id = tweet.id, auto_populate_reply_metadata = True)
        coun += 1
