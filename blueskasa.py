import requests
import urllib.request
import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time

# Páginas da NASA (IDs são substituídos por nomes de usuário para scraping)
nasa_pages = [
    "nasa",                # Página oficial da NASA
    "nasahubble",          # Página do Telescópio Espacial Hubble
    "nasaearth",           # Página de observação da Terra da NASA
    "nasajpl",             # Página do Jet Propulsion Laboratory
    "chandraxray",         # Página do Observatório de Raios-X Chandra
    "iss",                 # Página da Estação Espacial Internacional
    "nasawebb",            # Página do Telescópio James Webb
    "nasakennedy",         # Página do Kennedy Space Center
    "nasaames",            # Página do Ames Research Center
    "nasagoddard",         # Página do Goddard Space Center
    "nasa_marshall",       # Página do Marshall Space Center
    "nasastennis"          # Página do Stennis Space Center
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

# Função para baixar e salvar a última postagem do Instagram
def baixar_post(url_perfil, legendas_postadas):
    try:
        resposta = requests.get(url_perfil)
        resposta.raise_for_status()

        # Analisando o HTML da página
        soup = BeautifulSoup(resposta.text, 'lxml')

        # Buscando o script JSON com dados das postagens
        scripts = soup.find_all('script', type='text/javascript')
        data = None

        for script in scripts:
            if 'window._sharedData =' in script.string:
                json_data = script.string.split(' = ', 1)[1].rstrip(';')
                data = json.loads(json_data)
                break

        if not data:
            print("Não foi possível extrair dados do perfil.")
            return None, None

        # Extraindo postagens recentes
        posts = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']

        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

        for post in posts:
            node = post['node']
            media_date = datetime.fromtimestamp(node['taken_at_timestamp']).strftime('%Y-%m-%d')

            # Checando se a postagem é do dia anterior
            if media_date == yesterday and node['__typename'] == 'GraphImage':
                image_url = node['display_url']
                caption = node['edge_media_to_caption']['edges'][0]['node']['text'] if node['edge_media_to_caption']['edges'] else 'Sem legenda'

                # Verifica se a legenda já foi postada
                if caption in legendas_postadas:
                    print(f"Legenda já postada anteriormente: {caption}")
                    return None, None

                # Baixa e salva a imagem
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_path = f'imagem_{url_perfil.split("/")[-2]}.jpg'

                with open(image_path, 'wb') as f:
                    f.write(image_response.content)

                return image_path, caption

        print(f"Nenhuma mídia válida encontrada para {url_perfil}.")
        return None, None

    except Exception as e:
        print(f"Ocorreu um erro ao processar {url_perfil}: {e}")
        return None, None

# Carregar legendas já postadas
legendas_postadas = carregar_legendas_postadas()


# Inicializando o cliente do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky

api_key = os.environ.get("API_KEY")

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

mystring = f"""Astronomy Picture of the Day

{title}"""


if media_type == 'image':
    # Retrieve the image
    urllib.request.urlretrieve(site, 'apodtoday.jpeg')
    image_path = "apodtoday.jpeg"

elif media_type == 'video':
    # Retrieve the image
    urllib.request.urlretrieve(thumbs, 'apodtoday.jpeg')
    image_path = "apodtoday.jpeg"

else:
    print("sei la, deu ruim")
    



def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    resp = requests.post(
        pds_url + "/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def parse_uri(uri: str) -> Dict:
    repo, collection, rkey = uri.split("/")[2:5]
    return {"repo": repo, "collection": collection, "rkey": rkey}


def get_reply_refs(pds_url: str, parent_uri: str) -> Dict:
    uri_parts = parse_uri(parent_uri)
    resp = requests.get(
        pds_url + "/xrpc/com.atproto.repo.getRecord",
        params=uri_parts,
    )
    resp.raise_for_status()
    parent = resp.json()
    parent_reply = parent["value"].get("reply")

    if parent_reply:
        return {
            "root": parent_reply["root"],
            "parent": {"uri": parent["uri"], "cid": parent["cid"]},
        }
    else:
        return {
            "root": {"uri": parent["uri"], "cid": parent["cid"]},
            "parent": {"uri": parent["uri"], "cid": parent["cid"]},
        }


def split_text(text: str, max_length: int = 300) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += (word if current_chunk == "" else " " + word)
        else:
            chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def upload_file(pds_url: str, access_token: str, filename: str, img_bytes: bytes) -> Dict:
    suffix = filename.split(".")[-1].lower()
    mimetype = "application/octet-stream"
    if suffix in ["png"]:
        mimetype = "image/png"
    elif suffix in ["jpeg", "jpg"]:
        mimetype = "image/jpeg"
    elif suffix in ["webp"]:
        mimetype = "image/webp"

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": mimetype,
            "Authorization": "Bearer " + access_token,
        },
        data=img_bytes,
    )
    resp.raise_for_status()
    return resp.json()["blob"]


def upload_image(pds_url: str, access_token: str, image_path: str, alt_text: str) -> Dict:
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    if len(img_bytes) > 1000000:
        raise Exception(f"Imagem muito grande. Máximo permitido é 1000000 bytes, obtido: {len(img_bytes)}")

    blob = upload_file(pds_url, access_token, image_path, img_bytes)
    return {
        "$type": "app.bsky.embed.images",
        "images": [{"alt": alt_text or "", "image": blob}],
    }


def post_chunk(pds_url: str, access_token: str, did: str, text: str, reply_to: Dict = None, embed: Dict = None) -> Tuple[str, str]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }

    if reply_to:
        post["reply"] = reply_to

    if embed:
        post["embed"] = embed

    resp = requests.post(
        pds_url + "/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + access_token},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    resp.raise_for_status()
    response_data = resp.json()
    return response_data["uri"], response_data["cid"]


def post_thread(pds_url: str, handle: str, password: str, initial_text: str, long_text: str, image_path: str, alt_text: str):
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    # Posta o primeiro texto com a imagem
    embed = upload_image(pds_url, access_token, image_path, alt_text)
    uri, cid = post_chunk(pds_url, access_token, did, initial_text, embed=embed)

    # Posta o texto longo como uma thread
    chunks = split_text(long_text)
    reply_to = get_reply_refs(pds_url, uri)

    for chunk in chunks:
        uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to)
        reply_to = get_reply_refs(pds_url, uri)

    print("Thread postada com sucesso no Bluesky!")

def post_thread_with_image(pds_url: str, handle: str, password: str, long_text: str, image_path: str, alt_text: str):
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    # Corta o texto em chunks
    chunks = split_text(long_text)
    
    # Posta o primeiro chunk com a imagem
    embed = upload_image(pds_url, access_token, image_path, alt_text)
    uri, cid = post_chunk(pds_url, access_token, did, chunks[0], embed=embed)

    # Posta o restante dos chunks como thread
    reply_to = get_reply_refs(pds_url, uri)

    for chunk in chunks[1:]:
        uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to)
        reply_to = get_reply_refs(pds_url, uri)

    print("Thread com imagem postada com sucesso!")

pds_url = "https://bsky.social"
handle = BSKY_HANDLE
password = BSKY_PASSWORD
initial_text = mystring
long_text = explanation
image_path = image_path
alt_text = "Astronomy Picture of the Day"

post_thread(pds_url, handle, password, initial_text, long_text, image_path, alt_text)

# Processa cada página da NASA
for username in nasa_pages:
    url_perfil = f'https://www.instagram.com/{username}/'
    image_path, caption = baixar_post(url_perfil, legendas_postadas)    
 #   time.sleep(random.uniform(900, 1200))

    # Salvar a legenda se a imagem e legenda foram baixadas
    if caption and caption not in legendas_postadas:
        salvar_legenda_postada(caption)
        print(f"Imagem e legenda de {username} salvas com sucesso.")
        post_thread_with_image(pds_url, handle, password, caption, image_path, alt_text)
#        time.sleep(random.uniform(60, 120))
    else:
      print(f"Erro ao postar a imagem da {username} no Instagram")#: {e}")
