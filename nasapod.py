# coding=utf-8
import os
import sys
import urllib.request
import requests
import tweepy
import time
import google.generativeai as genai
from auth import api, client
from instagrapi import Client
import telebot
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import datetime, timedelta

# Authentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Choose a GenAI model (e.g., 'gemini-pro')
model = genai.GenerativeModel('gemini-pro')

# Get the picture, explanation, and/or video thumbnail
URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
    'api_key': api_key,
    'hd': 'True',
    'thumbs': 'True'
}
response = requests.get(URL_APOD, params=params).json()
site = response.get('url')
thumbs = response.get('thumbnail_url')
type = response.get('media_type')
explanation = response.get('explanation')
title = response.get('title')
hashtags = "#NASA #APOD #Astronomy #Space #Astrophotography"

# Função pra logar no Instagram
def post_instagram_photo(image_path, caption):
    try:
        cl = Client()
        cl.login(username, password)
        cl.photo_upload(image_path, caption)
        print("Foto publicada no Instagram")
    except Exception as e:
        print(f"Erro ao postar foto no Instagram: {e}")
        bot.send_message(tele_user, f"apodinsta com problema pra postar: {e}")

# Função para gerar conteúdo traduzido usando o modelo GenAI
def gerar_traducao(prompt):
    response = model.generate_content(prompt)
    if response.candidates and len(response.candidates) > 0:
        if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
            return response.candidates[0].content.parts[0].text
        else:
            print("Nenhuma parte de conteúdo encontrada na resposta.")
    else:
        print("Nenhum candidato válido encontrado.")
    return None

# Função para baixar a última postagem do Instagram da NASA e traduzi-la
def baixar_e_traduzir_post():
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    cl = Client()
    cl.login(username, password)
    medias = cl.user_medias(cl.user_id_from_username("nasa"), 10)
    for media in medias:
        media_date = media.taken_at.strftime('%Y-%m-%d')
        if media_date == yesterday and media.media_type == 1:
            image_url = media.thumbnail_url
            caption = media.caption_text
            prompt_nasa = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning: {caption}"
            traducao_nasa = gerar_traducao(prompt_nasa) or caption

            image_path = "imagem_nasa.jpg"
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path, traducao_nasa
            else:
                print("Erro ao baixar a imagem.")
                return None, None
    print("Nenhuma mídia válida encontrada.")
    return None, None

# Combinar o título e a explicação em um único prompt
prompt_combinado = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning:\n{title}\n{explanation}"

try:
    traducao_combinada = gerar_traducao(prompt_combinado)
    titulo_traduzido, explicacao_traduzida = traducao_combinada.split('\n', 1)

    insta_string = f"""Foto Astronômica do Dia
{titulo_traduzido}

{explicacao_traduzida}

Fonte: {site}

#NASA #APOD #Astronomia #Espaço #Astrofotografia"""

except AttributeError:
    insta_string = f"""Astronomy Picture of the Day
{title}

{explanation}

Source: {site}

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

# Função para baixar o vídeo e retornar o nome do arquivo baixado
def download_video(link):
    try:
        youtube_object = YouTube(link)
        video_stream = youtube_object.streams.get_highest_resolution()
        if video_stream:
            video_filename = video_stream.default_filename
            video_stream.download()
            return video_filename  # Retorna o nome do arquivo do vídeo baixado
        else:
            print("Nenhuma stream encontrada para o vídeo.")
            return None
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return None  # Retorna None se o download falhar

# Função para cortar o vídeo
def cortar_video(video_path, start_time, end_time, output_path):
    try:
        with VideoFileClip(video_path) as video:
            video_cortado = video.subclip(start_time, end_time)
            video_cortado.write_videofile(output_path, codec="libx264")
        return output_path
    except Exception as e:
        print(f"Erro ao cortar o vídeo: {e}")
        return None

# Check the type of media and post on Twitter and Instagram accordingly
tweet_id_imagem = None

if type == 'image':
    # Post the image on Twitter
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"
    media = api.media_upload(image)
    tweet_imagem = client.create_tweet(text=mystring, media_ids=[media.media_id])
    tweet_id_imagem = tweet_imagem.data['id']

    # Post the image on Instagram
    try:
        post_instagram_photo(image, insta_string)
    except Exception as e:
        print(f"Error posting photo on Instagram: {e}")
        bot.send_message(tele_user, 'apodinsta com problema pra postar imagem')

elif type == 'video':
    video_file = download_video(site)

    if video_file:
        video_file_cortado = cortar_video(video_file, 0, 60, "video_cortado.mp4")
        video_file_twitter = cortar_video(video_file, 0, 140, "video_twitter.mp4")
        if video_file_cortado:
            video_file = video_file_cortado
            video_twitter = video_file_twitter

        try:
            media = api.media_upload(video_twitter)
            tweet_video = client.create_tweet(text=mystring, media_category="tweet_video", media_ids=[media.media_id])
            tweet_id_imagem = tweet_video.data['id']
        except Exception as e:
            print(f"Erro ao postar vídeo no Twitter: {e}")

        try:
            post_instagram_photo(video_file, insta_string)
        except Exception as e:
            print(f"Erro ao postar vídeo no Instagram: {e}")
            bot.send_message(tele_user, 'apodinsta com problema pra postar video')

else:
    print("Tipo de mídia inválido.")
    bot.send_message(tele_user, 'Problema com o tipo de mídia no APOD')

tweet_ids_explicacao = []
reply_to_id = tweet_id_imagem

if tweet_id_imagem:
    for parte in chunks:
        try:
            response = client.create_tweet(text=str(parte), in_reply_to_tweet_id=reply_to_id)
            if 'id' in response.data:
                tweet_ids_explicacao.append(str(response.data['id']))
                reply_to_id = response.data['id']
            else:
                print(f"Error creating tweet: {response.data}")
        except Exception as e:
            print(f"Error creating tweet: {e}")
else:
    print("Erro: tweet_id_imagem não está definido.")

# Post the latest NASA image
nasa_image_path, nasa_caption = baixar_e_traduzir_post()
if nasa_image_path and nasa_caption:
    post_instagram_photo(nasa_image_path, nasa_caption)
