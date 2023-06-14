# coding=utf-8
import tweepy
import os
import sys
import urllib.request
import requests
from auth import api


# Autentication
api_key = os.environ.get("API_KEY")

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

{site}"""

# Decide whether is an image or a video and post

#if media == 'image':
#    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
#    image = "apodtoday.jpeg"
#    api.update_with_media(image, mystring)
#elif media == 'video':
#    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
#    video = 'apodvideo.jpeg'
#    api.update_with_media(video, mystring)
#else:
api.create_tweet(text = mystring)

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

#Make list with line lengths:
chunkex = [(n) for n in chunks]
coun = 0

# Post the explanation
while coun < len(chunkex):
    tweets = api.get_users_tweets(screen_name=api.me().screen_name, include_rts = False, exclude_replies = False ,count=1)
    for tweet in tweets:
        api.update_status(str(chunkex[coun]), in_reply_to_status_id = tweet.id, auto_populate_reply_metadata = True)
        coun += 1
