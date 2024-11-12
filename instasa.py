# coding=utf-8
import os
import urllib.request
import requests
import google.generativeai as genai
from instagrapi import Client
import telebot
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
import random
import time
from sys import exit

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

# Função para logar no Instagram com verificação de desafio
def logar_instagram():
    cl = Client()
    session_file = 'instagram_session.json'
    try:
        if os.path.exists(session_file):
            cl.load_settings(session_file)
        cl.login(username, password)
        cl.get_timeline_feed()
        cl.dump_settings(session_file)
    except Exception as e:
        print(f"Erro ao logar no Instagram: {e}")
        bot.send_message(tele_user, f"apodinsta erro ao logar no Instagram: {e}")
        exit()
    return cl

try:
    instagram_client = logar_instagram()
except Exception as e:
    print(f"Erro ao logar no Instagram: {e}")
    bot.send_message(tele_user, f"Erro ao logar no Instagram: {e}")

# Função para postar foto no Instagram
def post_instagram_photo(cl, image_path, caption):
    try:
        time.sleep(random.uniform(30, 60))  # Espera aleatória antes de postar
        cl.photo_upload(image_path, caption)
        print("Foto publicada no Instagram")
    except Exception as e:
        print(f"Erro ao postar foto no Instagram: {e}")
        bot.send_message(tele_user, f"apodinsta com problema pra postar: {e}")

# Função para postar vídeo no Instagram
def post_instagram_video(cl, video_path, caption):
    try:
        time.sleep(random.uniform(30, 60))  # Espera aleatória antes de postar
        cl.video_upload(video_path, caption)
        print("Vídeo publicado no Instagram")
    except Exception as e:
        print(f"Erro ao postar vídeo no Instagram: {e}")
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

# Função para baixar o vídeo e retornar o nome do arquivo baixado
def download_video(link):
    try:
        youtube_object = YouTube(link)
        video_stream = youtube_object.streams.get_highest_resolution()
        if video_stream:
            video_filename = video_stream.default_filename
            video_stream.download()
            time.sleep(random.uniform(1, 5))  # Espera aleatória para evitar sobrecarga de rede
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
            duration = video.duration
            if start_time < 0 or end_time > duration:
                raise ValueError("Os tempos de corte estão fora da duração do vídeo")
            video_cortado = video.subclip(start_time, end_time)
            video_cortado.write_videofile(output_path, codec="libx264")
        return output_path
    except Exception as e:
        print(f"Erro ao cortar o vídeo: {e}")
        return None


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

# Combinar o título e a explicação em um único prompt
prompt_combinado = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning and based on the following text, create engaging astronomy related hashtags:\n{title}\n\n{explanation}"

# Gerar tradução combinada usando o modelo
try:
    traducao_combinada = gerar_traducao(prompt_combinado)
    if traducao_combinada:
        insta_string = f"""Foto Astronômica do Dia
{title}

{traducao_combinada}"""

    else:
        raise AttributeError("A tradução combinada não foi gerada.")
except AttributeError as e:
    print(f"Erro ao gerar a tradução: {e}")
    insta_string = f"""Foto Astronômica do Dia
{title}

{explanation}

#NASA #APOD #Astronomia #Espaço #Astrofotografia"""

print(insta_string)


if media_type == 'image':
    # Retrieve the image
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"

    # Post the image on Instagram
    if instagram_client:
        try:
            post_instagram_photo(instagram_client, image, insta_string)
        except Exception as e:
            print(f"Erro ao postar foto no Instagram: {e}")
            bot.send_message(tele_user, 'apodinsta com problema pra postar imagem')

elif media_type == 'video':
    # Retrieve the video
    video_file = download_video(site)
    
    if video_file:
        video_file_cortado = cortar_video(video_file, 0, 60, "video_cortado.mp4")
        if video_file_cortado:
            video_file = video_file_cortado
            # Post the video on Instagram
            if instagram_client:
                try:
                    post_instagram_video(instagram_client, video_file, insta_string)
                except Exception as e:
                    print(f"Erro ao postar vídeo no Instagram: {e}")
                    bot.send_message(tele_user, 'apodinsta com problema pra postar video')

else:
    print("Tipo de mídia inválido.")
    bot.send_message(tele_user, 'Problema com o tipo de mídia no APOD')
