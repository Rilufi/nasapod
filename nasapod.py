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
from threadspy import ThreadsAPI

# Authentication
api_key = os.environ.get("API_KEY")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
tele_user = os.environ.get("TELE_USER")
TOKEN = os.environ["TELEGRAM_TOKEN"]
bot = telebot.TeleBot(TOKEN)
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
thrd = ThreadsAPI(username=username, password=password)

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
media_type = response.get('media_type')
explanation = response.get('explanation')
title = response.get('title')
hashtags = "#NASA #APOD #Astronomy #Space #Astrophotography"

# Função para logar no Instagram
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

# Função para baixar a última postagem do Instagram da NASA
def baixar_post_nasa():
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    cl = Client()
    cl.login(username, password)
    medias = cl.user_medias(cl.user_id_from_username("nasa"), 10)
    for media in medias:
        media_date = media.taken_at.strftime('%Y-%m-%d')
        if media_date == yesterday and media.media_type == 1:
            image_url = media.thumbnail_url
            caption = media.caption_text

            image_path = "imagem_nasa.jpg"
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path, caption
            else:
                print("Erro ao baixar a imagem.")
                return None, None
    print("Nenhuma mídia válida encontrada.")
    return None, None

# Função para dividir o texto em múltiplos tweets
def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

# Função para postar a imagem da NASA no Twitter com a legenda original
def post_nasa_photo_on_twitter(image_path, caption):
    try:
        media = api.media_upload(image_path)
        tweet = client.create_tweet(text=caption[:280], media_ids=[media.media_id])
        tweet_id = tweet.data['id']
        print("Foto da NASA publicada no Twitter")

        # Postar o restante da legenda em uma thread
        chunks = list(get_chunks(caption[280:], 280))
        reply_to_id = tweet_id
        for parte in chunks:
            try:
                response = client.create_tweet(text=str(parte), in_reply_to_tweet_id=reply_to_id)
                if 'id' in response.data:
                    reply_to_id = response.data['id']
                    print("Tweet publicado como parte da thread da NASA")
                else:
                    print(f"Error creating tweet: {response.data}")
            except Exception as e:
                print(f"Error creating tweet: {e}")
    except Exception as e:
        print(f"Erro ao postar foto da NASA no Twitter: {e}")

# Combinar o título e a explicação em um único prompt
prompt_combinado = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning:\n{title}\n{explanation}"

try:
    traducao_combinada = gerar_traducao(prompt_combinado)
    if traducao_combinada:
        titulo_traduzido, explicacao_traduzida = traducao_combinada.split('\n', 1)

        insta_string = f"""Foto Astronômica do Dia
{titulo_traduzido}

{explicacao_traduzida}

Fonte: {site}

#NASA #APOD #Astronomia #Espaço #Astrofotografia"""

        thrd_string = f"""Foto Astronômica do Dia
{titulo_traduzido}

Fonte: {site}

#NASA #APOD #Astronomia #Espaço #Astrofotografia"""

    else:
        raise AttributeError("A tradução combinada não foi gerada.")
except AttributeError as e:
    print(f"Erro ao gerar a tradução: {e}")
    insta_string = f"""Astronomy Picture of the Day
{title}

{explanation}

Source: {site}

{hashtags}"""

    thrd_string = f"""Astronomy Picture of the Day
{title}

Source: {site}

{hashtags}"""

print(insta_string)

mystring = f"""Astronomy Picture of the Day

{title}

Source: {site}

{hashtags}"""

myexstring = f"""{explanation}"""

chunks = list(get_chunks(explanation, 280))

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

if media_type == 'image':
    # Retrieve the image
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"

    # Post the image on Threads
    try:
        thrd.publish(caption=thrd_string, image_path=image)
        print("Foto publicada no Threads")
    except Exception as e:
        print(f"Erro ao postar foto no Threads: {e}")
        bot.send_message(tele_user, f"Erro ao postar no Threads: {e}")
    
    # Post the image on Twitter
    try:
        media = api.media_upload(image)
        tweet_imagem = client.create_tweet(text=mystring, media_ids=[media.media_id])
        tweet_id_imagem = tweet_imagem.data['id']
    except Exception as e:
        print(f"Erro ao postar foto no Twitter: {e}")

    # Post the image on Instagram
    try:
        post_instagram_photo(image, insta_string)
    except Exception as e:
        print(f"Erro ao postar foto no Instagram: {e}")
        bot.send_message(tele_user, 'apodinsta com problema pra postar imagem')

elif media_type == 'video':
    # Retrieve the video
    video_file = download_video(site)
    
    # Retrieve the thumbs
    urllib.request.urlretrieve(thumbs, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"

    # Post the image on Threads
    try:
        thrd.publish(caption=thrd_string, image_path=image)
        print("Thumbnail do vídeo publicada no Threads")
    except Exception as e:
        print(f"Erro ao postar thumbnail do vídeo no Threads: {e}")
        bot.send_message(tele_user, f"Erro ao postar no Threads: {e}")

    if video_file:
        video_file_cortado = cortar_video(video_file, 0, 60, "video_cortado.mp4")
        video_file_twitter = cortar_video(video_file, 0, 140, "video_twitter.mp4")
        if video_file_cortado:
            video_file = video_file_cortado
            video_twitter = video_file_twitter

        # Post the video on Twitter
        try:
            media = api.media_upload(video_twitter)
            tweet_video = client.create_tweet(text=mystring, media_category="tweet_video", media_ids=[media.media_id])
            tweet_id_imagem = tweet_video.data['id']
            print("Vídeo publicado no Twitter")
        except Exception as e:
            print(f"Erro ao postar vídeo no Twitter: {e}")

        # Post the video on Instagram
        try:
            post_instagram_photo(video_file, insta_string)
        except Exception as e:
            print(f"Erro ao postar vídeo no Instagram: {e}")
            bot.send_message(tele_user, 'apodinsta com problema pra postar video')

else:
    print("Tipo de mídia inválido.")
    bot.send_message(tele_user, 'Problema com o tipo de mídia no APOD')

# Publicar explicações no Twitter como uma thread
tweet_ids_explicacao = []
reply_to_id = tweet_id_imagem

if tweet_id_imagem:
    for parte in chunks:
        try:
            response = client.create_tweet(text=str(parte), in_reply_to_tweet_id=reply_to_id)
            if 'id' in response.data:
                tweet_ids_explicacao.append(str(response.data['id']))
                reply_to_id = response.data['id']
                print("Tweet publicado como parte da thread")
            else:
                print(f"Error creating tweet: {response.data}")
        except Exception as e:
            print(f"Error creating tweet: {e}")
else:
    print("Erro: tweet_id_imagem não está definido.")

# Baixar e postar a última imagem da NASA no Instagram
nasa_image_path, nasa_caption = baixar_post_nasa()
if nasa_image_path and nasa_caption:
    try:
        post_instagram_photo(nasa_image_path, nasa_caption)
        post_nasa_photo_on_twitter(image_path, caption)  # Postar no Twitter com a legenda original
    except Exception as e:
        print(f"Erro ao postar a imagem da NASA no Instagram ou Twitter: {e}")
        bot.send_message(tele_user, 'apodinsta com problema pra postar imagem da NASA')

# Adicionar log de conclusão
print("Script concluído.")
