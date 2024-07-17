# coding=utf-8
import os
import urllib.request
import requests
import tweepy
import google.generativeai as genai
from auth import api, client
from instagrapi import Client
import telebot
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from datetime import datetime, timedelta
from threadspy import ThreadsAPI
import random
import time

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

# Páginas da NASA
nasa_pages = [
    528817151,   # Página oficial da NASA
    5951848929,  # Página do Telescópio Espacial Hubble
    354812686,   # Página de observação da Terra da NASA
    582986390,   # Página do Jet Propulsion Laboratory
    1332348075,  # Página do Observatório de Raios-X Chandra
    953293389,   # Página da Estação Espacial Internacional
    549313808,   # Página do Telescópio James Webb
    549403870,   # Página do Kennedy Space Center
    182988865,   # Página do Ames Research Center
    3808579,     # Página do Goddard Space Center
    757149008,   # Página do Marshall Space Center
    694816689    # Página do Stennis Space Center
]

# Caminho para o arquivo de legendas
legendas_file = "legendas_postadas.txt"

# Função para carregar legendas postadas
def carregar_legendas_postadas():
    if os.path.exists(legendas_file):
        with open(legendas_file, "r", encoding="utf-8") as file:
            return set(file.read().splitlines())
    return set()

# Função para salvar legenda postada
def salvar_legenda_postada(legenda):
    with open(legendas_file, "a", encoding="utf-8") as file:
        file.write(legenda + "\n")

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
        bot.send_message(tele_user, f"Erro ao logar no Instagram: {e}")
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

# Função para baixar e traduzir a última postagem do Instagram da NASA
def baixar_e_traduzir_post(cl, username, legendas_postadas):
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    medias = cl.user_medias(username, 5)
    for media in medias:
        media_date = media.taken_at.strftime('%Y-%m-%d')
        if media_date == yesterday and media.media_type == 1:
            image_url = media.thumbnail_url
            caption = media.caption_text
            if caption in legendas_postadas:
                print(f"Legenda já postada anteriormente: {caption}")
                return None, None, None  # Adicionado para garantir que não poste novamente
            prompt_nasa = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning: {caption}"
            traducao_nasa = gerar_traducao(prompt_nasa)
            if traducao_nasa:
                image_path = f"imagem_{username}.jpg"
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    return image_path, traducao_nasa, caption
                else:
                    print(f"Erro ao baixar a imagem de {username}.")
                    return None, None, None
            else:
                print("Não foi possível traduzir a legenda.")
                return None, None, None
    print(f"Nenhuma mídia válida encontrada para {username}.")
    return None, None, None

# Carregar legendas já postadas
legendas_postadas = carregar_legendas_postadas()

# Baixar e postar a última imagem de cada página da NASA no Instagram
if instagram_client:
    for page in nasa_pages:
        nasa_image_path, nasa_caption, original_caption = baixar_e_traduzir_post(instagram_client, page, legendas_postadas)
        if nasa_image_path and nasa_caption:
            try:
                post_instagram_photo(instagram_client, nasa_image_path, nasa_caption)
                # Salvar a legenda original no arquivo
                salvar_legenda_postada(original_caption)
                time.sleep(random.uniform(60, 120))  # Espera aleatória entre posts
            except Exception as e:
                print(f"Erro ao postar a imagem da {page} no Instagram: {e}")
                bot.send_message(tele_user, f"apodinsta com problema pra postar imagem da {page}")

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

# Função para dividir o texto em múltiplos tweets
def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end + 1
    yield s[start:]

# Get the picture, explanation, and/or video thumbnail
URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
    'api_key': api_key,
    'hd': 'True',
    'thumbs': 'True'
}
response = requests.get(URL_APOD, params=params)
data = response.json()

# Check if there's a URL for an image
if "url" in data and data["url"].endswith((".jpg", ".jpeg", ".png")):
    url_image = data["hdurl"]
    urllib.request.urlretrieve(url_image, "image.jpg")
    midia = "image.jpg"
    tipo = "photo"
    print("Imagem APOD obtida")
else:
    url_image = None

# If there's no image, check for a video thumbnail
if not url_image and "thumbnail_url" in data:
    url_image = data["thumbnail_url"]
    urllib.request.urlretrieve(url_image, "image.jpg")
    print("Miniatura de vídeo APOD obtida")

# Process the explanation
apod_exp = data.get("explanation", "")
if apod_exp:
    prompt = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning: {apod_exp}"
    traducao = gerar_traducao(prompt)
else:
    traducao = None

# Postar no Twitter
if url_image and traducao:
    try:
        media = api.media_upload("image.jpg")
        tweet_parts = list(get_chunks(traducao, 280))
        tweet = tweet_parts.pop(0)
        status = api.update_status(status=tweet, media_ids=[media.media_id])
        while tweet_parts:
            time.sleep(random.uniform(15, 30))  # Espera aleatória antes de postar
            tweet = tweet_parts.pop(0)
            status = api.update_status(status=tweet, in_reply_to_status_id=status.id, auto_populate_reply_metadata=True)
        print("Postagem APOD feita no Twitter")
    except Exception as e:
        print(f"Erro ao postar no Twitter: {e}")
        bot.send_message(tele_user, f"apodtw com problema pra postar: {e}")

# Postar no Instagram
if instagram_client and url_image and traducao:
    try:
        post_instagram_photo(instagram_client, "image.jpg", traducao)
        print("Postagem APOD feita no Instagram")
    except Exception as e:
        print(f"Erro ao postar no Instagram: {e}")
        bot.send_message(tele_user, f"apodinsta com problema pra postar: {e}")

# Postar no Threads
if url_image and traducao:
    try:
        thrd.post_thread(traducao, image_paths=["image.jpg"])
        print("Postagem APOD feita no Threads")
    except Exception as e:
        print(f"Erro ao postar no Threads: {e}")
        bot.send_message(tele_user, f"apodthreads com problema pra postar: {e}")

# Postar vídeo no Instagram (Exemplo)
link_video = "https://www.youtube.com/watch?v=example"  # URL do vídeo do YouTube
video_filename = download_video(link_video)
if video_filename:
    video_path_cortado = cortar_video(video_filename, start_time=10, end_time=60, output_path="video_cortado.mp4")
    if video_path_cortado and traducao:
        post_instagram_video(instagram_client, video_path_cortado, traducao)
        print("Vídeo APOD postado no Instagram")
