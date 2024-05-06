# coding=utf-8
import os
import urllib.request
import requests
import tweepy
import time
import google.generativeai as genai
from auth import api, client
from instagrapi import Client
import telebot
from pytube import YouTube


# Authentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)
GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Choose a GenAI model (e.g., 'gemini-pro')
model = genai.GenerativeModel('gemini-pro')

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

# Função para gerar conteúdo traduzido usando o modelo GenAI
def gerar_traducao(prompt):
        response = model.generate_content(prompt)
        # Verifique se a resposta contém candidatos e se a lista não está vazia
        if response.candidates and len(response.candidates) > 0:
            if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
                return response.candidates[0].content.parts[0].text
            else:
                print("Nenhuma parte de conteúdo encontrada na resposta.")
        else:
            print(f"Nenhum candidato válido encontrado, tentando novamente... ({retries+1}/{max_retries})")
    
# Combinar o título e a explicação em um único prompt
prompt_combinado = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning:\nTitle: {title}\nExplanation: {explanation}"

try:
	traducao_combinada = gerar_traducao(prompt_combinado)
	# Separe a tradução combinada em título e explicação
	titulo_traduzido, explicacao_traduzida = traducao_combinada.split('\n', 1)

	# Use as traduções na string do Instagram
	insta_string = f"""Foto Astronômica do Dia
{titulo_traduzido}

{explicacao_traduzida}

Fonte: {site}

{hashtags}"""
except AttributeError:
	insta_string = f"""Foto Astronômica do Dia
{title}

{explanation}

Fonte: {site}

{hashtags}"""
	
print(insta_string)

mystring = f"""Astronomy Picture of the Day

{title}

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

def download(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")

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
        bot.send_message(tele_user, 'apod com problema')

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
	video = download(site)
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
