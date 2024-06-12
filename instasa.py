# coding=utf-8
import os
import urllib.request
import requests
import google.generativeai as genai
from instagrapi import Client
import telebot
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

# Páginas da NASA
nasa_pages = [
    "nasa",  # Página oficial da NASA
    "nasahubble",  # Página do Telescópio Espacial Hubble
    "nasaearth",  # Página de observação da Terra da NASA
    "nasajpl",  # Página do Jet Propulsion Laboratory
    "nasachandraxray",  # Página do Observatório de Raios-X Chandra
    "iss",  # Página da Estação Espacial Internacional
    "nasawebb", # Página do Telescópio James Webb
    "nasakennedy", # Página do Kennedy Space Center
    "nasaames", # Página do Ames Research Center
    "nasagoddard", # Página do Goddard Space Center
    "nasa_marshall", # Página do Marshall Space Center
    "nasastennis" # Página do Stennis Space Center
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

# Função para baixar e traduzir a última postagem do Instagram da NASA
def baixar_e_traduzir_post(cl, username, legendas_postadas):
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    medias = cl.user_medias(cl.user_id_from_username(username), 10)
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

# Get the picture, explanation, and/or video thumbnail
URL_APOD = "https://api.nasa.gov/planetary/apod"
params = {
    'api_key': api_key,
    'hd': 'True',
    'thumbs': 'True'
}
response = requests.get(URL_APOD, params=params).json()
site = response.get('url')
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
    else:
        raise AttributeError("A tradução combinada não foi gerada.")
except AttributeError as e:
    print(f"Erro ao gerar a tradução: {e}")
    insta_string = f"""Astronomy Picture of the Day
{title}

{explanation}

Source: {site}

{hashtags}"""

print(insta_string)

if media_type == 'image':
    # Retrieve the image
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image = "apodtoday.jpeg"

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

    if video_file:
        # Post the video on Instagram
        try:
            instagram_client = logar_instagram()
            post_instagram_photo(instagram_client, video_file, insta_string)
        except Exception as e:
            print(f"Erro ao postar vídeo no Instagram: {e}")
            bot.send_message(tele_user, 'apodinsta com problema pra postar video')

else:
    print("Tipo de mídia inválido.")
    bot.send_message(tele_user, 'Problema com o tipo de mídia no APOD')

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
for page in nasa_pages:
    nasa_image_path, nasa_caption, original_caption = baixar_e_traduzir_post(instagram_client, page, legendas_postadas)
    if nasa_image_path and nasa_caption:
        try:
            post_instagram_photo(instagram_client, nasa_image_path, nasa_caption)
            # Salvar a legenda original no arquivo
            salvar_legenda_postada(original_caption)
        except Exception as e:
            print(f"Erro ao postar a imagem da {page} no Instagram: {e}")
            bot.send_message(tele_user, f"apodinsta com problema pra postar imagem da {page}")

# Adicionar log de conclusão
print("Script concluído.")
