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

# Definir uma lista para armazenar os IDs dos tweets
tweet_ids = []

# Postar cada parte do texto e armazenar os IDs dos tweets
for parte in chunkex:
    # Tentar criar o tweet manualmente
    try:
        response = client.create_tweet(text=str(parte))
        if 'id' in response.data:
            tweet_ids.append(str(response.data['id']))  # Convertendo para string
        else:
            print(f"Erro ao postar tweet: {response.data}")
    except Exception as e:
        print(f"Erro ao postar tweet: {e}")

# Gerar URLs para os tweets publicados
urls_tweets = [f"https://twitter.com/nasobot/status/{tweet_id}" for tweet_id in tweet_ids]


mystring = f"""Astronomy Picture of the Day

{title}

Fonte: {site}"""


# Decide whether is an image or a video and post on Twitter and Instagram
if type == 'image':
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    media = api.media_upload(image)
    try:
        # Postar o tweet e obter o ID
        response = client.create_tweet(text=mystring, media_ids=[media.media_id])
        if 'id' in response:
            # Adicionar o ID do tweet à lista de IDs
            tweet_ids.append(str(response['id']))  # Convertendo para string
        else:
            print(f"Erro ao postar tweet adicional: {response}")
    except Exception as e:
        print(f"Erro ao postar tweet adicional: {e}")
    # Adicionar o ID do tweet da imagem à lista de IDs
    tweet_ids.append(str(response['id']))
    try:
      cl.photo_upload(image, insta_string)
      print("foto publicada no insta")
    except:
      with Image.open("apodtoday") as im:
        rgb_im = im.convert('RGB')
        rgb_im.save('apodtoday.jpg')
      cl.photo_upload("apodtoday.jpg", insta_string)
    print("gif convertido e postado")
elif type == 'video':
    urllib.request.urlretrieve(thumbs, 'apodvideo.jpeg')
    video = 'apodvideo.jpeg'
    media = api.media_upload(video)
    try:
        # Postar o tweet e obter o ID
        response = client.create_tweet(text=mystring, media_ids=[media.media_id])
        if 'id' in response:
            # Adicionar o ID do tweet à lista de IDs
            tweet_ids.append(str(response['id']))  # Convertendo para string
        else:
            print(f"Erro ao postar tweet adicional: {response}")
    except Exception as e:
        print(f"Erro ao postar tweet adicional: {e}")

    # Adicionar o ID do tweet da imagem à lista de IDs
    tweet_ids.append(str(response['id']))
else:
    print("deu ruim")
    bot.send_message(tele_user,  'apod com problema')

# Concatenar os URLs dos tweets em um tweet encadeado
tweet_encadeado = "The official NASA explanation for today's Astronomy Picture of the Day (APOD) can be found in the tweet sequence below: " + "\n".join(urls_tweets)

# Publicar o tweet encadeado
client.create_tweet(text=tweet_encadeado)
