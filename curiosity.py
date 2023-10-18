import tweepy
import os
import sys
import urllib.request
import requests
from auth import api, client
import datetime
from instagrapi import Client
import telebot
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import math


today = datetime.date.today()
hoje = today.strftime('%Y-%m-%d')
ontem = '2023-10-16'
api_key = os.environ["API_KEY"]
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)

##logging instagram
try:
      cl = Client(request_timeout=7)
      cl.login(username, password)
      print('instapod logado')
except:
      print('instapod deslogado')
      bot.send_message(tele_user,  'apod com problema')
      pass


def formatImage(image):
    base = Image.new('RGB', (1080,1920), (255,255,0))
    cat = Image.open(image)
    originalCat = cat.copy()

    #~ Resize and spawn multiple image of cat in the background
    wPercent = (216/float(originalCat.size[0]))
    hSize = int((float(originalCat.size[1])*float(wPercent)))
    smallCat = originalCat.resize((216,hSize), Image.LANCZOS)#Resampling.LANCZOS)

    #~ Reduce brightness & blur, goal is to put in foreground the main cat
    smallCat = ImageEnhance.Brightness(smallCat).enhance(.75)
    smallCat = smallCat.filter(ImageFilter.GaussianBlur(4))

    for i in range( math.ceil(base.size[1]/hSize) ):
        for j in range( math.ceil(base.size[0]/smallCat.size[0]) ):
            base.paste(smallCat, (j*smallCat.size[0],i*smallCat.size[1]))

    #~ Resize the image to fit, if it's too large (>1000) or too small (<800)
    if cat.size[0] > 1000 or cat.size[0] < 800:
        wPercent = (1000/float(cat.size[0]))
        hSize = int((float(cat.size[1])*float(wPercent)))
        cat = cat.resize((1000,hSize), Image.LANCZOS)#Resampling.LANCZOS)

    wPos = int((1080-cat.size[0])/2)
    hPos = int((1920-cat.size[1])/2)

    base.paste(cat, (wPos, hPos))
    base.save(image, quality=95)
    

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

        insta_string = f"""  Latest {rover_name} Rover Picture
Taken from the {camera} on Sol {sol}"""
        
        urllib.request.urlretrieve(site, 'rovertoday.jpeg')
        image = "rovertoday.jpeg"
        media = api.media_upload(image)
        client.create_tweet(text=mystring, media_ids=[media.media_id])
        print(mystring)
        formatImage('rovertoday.jpeg')
        cl.photo_upload_to_story('rovertoday.jpeg',insta_string)
    else:
        print(f'Sem {rover_name} hoje')
        pass

rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/", 'Curiosity')
rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/", 'Perseverance')
rover_pic("https://api.nasa.gov/mars-photos/api/v1/rovers/spirit/", 'Spirit')
