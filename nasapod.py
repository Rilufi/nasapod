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

mystring = f""" Astronomy Picture of the Day

{title}

Source: {site}"""

insta_string = f""" Astronomy Picture of the Day
{title}

{explanation}

Source: {site}
#Astronomy #Space #Universe #Astrophotography #Cosmos #Stars #Galaxy #NASA #Science #NightSky"""

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
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

chunks = get_chunks(explanation, 280)

# Make list with line lengths
chunkex = [(n) for n in chunks]


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

# Posta cada parte da explicação como um reply para o tweet da imagem
tweet_ids_explicacao = []
reply_id_anterior = tweet_id_imagem
for parte in chunkex:
    # Posta a parte da explicação como reply
    tweet_explicacao = client.create_tweet(text=str(parte), in_reply_to=reply_id_anterior)
    
    # Salva o ID do tweet de explicação
    tweet_ids_explicacao.append(tweet_explicacao['id'])
    
    # Atualiza o ID do tweet anterior para o próximo reply
    reply_id_anterior = tweet_explicacao['id']

# Concatena os IDs dos tweets de explicação em uma lista para referência posterior
tweet_ids_total = [tweet_id_imagem] + tweet_ids_explicacao

# Verifica se todos os tweets foram postados corretamente
if all(tweet_id is not None for tweet_id in tweet_ids_total):
    print("Todos os tweets foram postados com sucesso.")
else:
    print("Houve um erro ao postar os tweets.")
