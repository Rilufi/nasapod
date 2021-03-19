# coding=utf-8

import tweepy
import os
import sys
from nasa import apod
import urllib.request
from credentials import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

os.environ['NASA_API_KEY'] = nasa_key

picture = apod.apod()
site = str(picture.url)
explanation = str(picture.explanation)

urllib.request.urlretrieve(site, 'apodtoday.jpeg')


toReply = "user" #user to get most recent tweet

site = picture.url
title = picture.title

mystring = f""" Astronomy Picture of the Day

{title}

Fonte: {site}"""

image = "apodtoday.jpeg"

try:
    api.update_with_media(image, mystring)
except:
    api.update_status(mystring)

myexstring = f"""{explanation}"""


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


while coun < len(chunkex):
    tweets = api.user_timeline(screen_name = toReply, count=1)
    for tweet in tweets:
        api.update_status(str(chunkex[coun]), in_reply_to_status_id = tweet.id, auto_populate_reply_metadata = True)
        coun += 1
