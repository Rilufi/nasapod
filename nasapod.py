# coding=utf-8
import os
import time
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
from random import randint

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

# User IDs da NASA (obtenha-os uma vez e reutilize)
nasa_user_ids = [
    528817151,  # Página oficial da NASA
    178744053,  # Página do Telescópio Espacial Hubble
    1822906088,  # Página de observação da Terra da NASA
    2123060486,  # Página do Jet Propulsion Laboratory
    295889392,  # Página do Observatório de Raios-X Chandra
    250004703,  # Página da Estação Espacial Internacional
    2490770335, # Página do Telescópio James Webb
    358206989, # Página do Kennedy Space Center
    2293841650, # Página do Ames Research Center
    3309599688, # Página do Goddard Space Center
    184465477, # Página do Marshall Space Center
    3390995610 # Página do Stennis Space Center
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

# Função para logar no Instagram
def logar_instagram():
    cl = Client()
    cl.login(username, password)
    return cl

# Função para postar foto no Instagram
def post_instagram_photo(cl, image_path, caption):
    try:
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

# Função para lidar com erros 429 (Too Many Requests)
def retry_on_429(func):
    def wrapper(*args, **kwargs):
        retries = 5
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Too Many Requests: Retrying after a delay")
                    time.sleep(60)  # Espera 1 minuto antes de tentar novamente
                else:
                    raise
        print("Max retries reached. Exiting.")
        return None
    return wrapper

# Função para baixar a última postagem do Instagram da NASA e traduzi-la
@retry_on_429
def baixar_e_traduzir_post(cl, user_id, legendas_postadas):
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    medias = cl.user_medias(user_id, 10)
    for media in medias:
        media_date = media.taken_at.strftime('%Y-%m-%d')
        if media_date == yesterday and media.media_type == 1:
            image_url = media.thumbnail_url
            caption = media.caption_text
            if caption in legendas_postadas:
                print(f"Legenda já postada anteriormente: {caption}")
                continue
            prompt_nasa = f"Given the following scientific text from a reputable source (NASA) in English, translate it accurately and fluently into grammatically correct Brazilian Portuguese while preserving the scientific meaning: {caption}"
            traducao_nasa = gerar_traducao(prompt_nasa)
            if traducao_nasa:
                image_path = f"imagem_{user_id}.jpg"
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    return image_path, traducao_nasa, caption
                else:
                    print(f"Erro ao baixar a imagem do usuário {user_id}.")
                    return None, None, None
            else:
                print("Não foi possível traduzir a legenda.")
                return None, None, None
    print(f"Nenhuma mídia válida encontrada para o usuário {user_id}.")
    return None, None, None

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
response = requests.get(URL_APOD, params=params).json()
site = response.get('url')
thumbs = response.get('thumbnail_url')
media_type = response.get('media_type')
explanation = response.get('explanation')
title = response.get('title')
hashtags = "#NASA #APOD #Astronomy #Space #Astrophotography"

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
        instagram_client = logar_instagram()
        post_instagram_photo(instagram_client, image, insta_string)
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
            post_instagram_photo(instagram_client, video_file, insta_string)
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

# Carregar legendas já postadas
legendas_postadas = carregar_legendas_postadas()

# Verificar se a tradução da APOD foi bem-sucedida antes de postar
if traducao_combinada:
    try:
        post_instagram_photo(instagram_client, image, insta_string)
    except Exception as e:
        print(f"Erro ao postar a imagem da APOD no Instagram: {e}")
        bot.send_message(tele_user, 'apodinsta com problema pra postar imagem da APOD')

# Baixar e postar a última imagem de cada página da NASA no Instagram
for user_id in nasa_user_ids:
    nasa_image_path, nasa_caption, original_caption = baixar_e_traduzir_post(instagram_client, user_id, legendas_postadas)
    if nasa_image_path and nasa_caption:
        try:
            post_instagram_photo(instagram_client, nasa_image_path, nasa_caption)
            # Salvar a legenda original no arquivo
            salvar_legenda_postada(original_caption)
            # Esperar um tempo aleatório entre 30 a 90 segundos para evitar parecer um bot
            time.sleep(randint(30, 90))
        except Exception as e:
            print(f"Erro ao postar a imagem da NASA no Instagram: {e}")
            bot.send_message(tele_user, f"apodinsta com problema pra postar imagem da NASA")

# Adicionar log de conclusão
print("Script concluído.")
