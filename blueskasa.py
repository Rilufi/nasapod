import requests
import urllib.request
import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import os
from PIL import Image

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
thumbs = response.get('thumbnail_url')
media_type = response.get('media_type')
explanation = response.get('explanation')
title = response.get('title')

# Função para gerar a URL do APOD do dia
def get_apod_url() -> str:
    today = datetime.now()
    yymmdd = today.strftime("%y%m%d")  # Formato yymmdd
    apod_url = f"https://apod.nasa.gov/apod/ap{yymmdd}.html"
    return apod_url

# URL do APOD
site = get_apod_url()

# Modifica o mystring para incluir o link como hipertexto
mystring = f"""Astronomy Picture of the Day

{title}

Source: {site}"""

# Função para criar facets de rich text para o link
def create_link_facets(text: str, link_text: str, url: str) -> List[Dict]:
    byte_start = text.index(link_text)
    byte_end = byte_start + len(link_text)
    return [{
        "index": {
            "byteStart": byte_start,
            "byteEnd": byte_end
        },
        "features": [{
            "$type": "app.bsky.richtext.facet#link",
            "uri": url
        }]
    }]

# Gera as facets para o link da APOD
facets = create_link_facets(mystring, site, site)

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
    

# Function to resize image for Bluesky
def resize_bluesky(image_path, max_file_size=1 * 1024 * 1024):
    img = Image.open(image_path)

    if os.path.getsize(image_path) > max_file_size:
        img.thumbnail((1600, 1600))
        quality = 95
        while os.path.getsize(image_path) > max_file_size and quality > 10:
            img.save(image_path, quality=quality)
            quality -= 5
            img = Image.open(image_path)

        print(f"Imagem redimensionada e comprimida para o limite do Bluesky de {max_file_size} bytes.")
    else:
        img.save(image_path)
        print("Imagem já está dentro do limite de tamanho do Bluesky.")

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

# Modificação para incluir facets na postagem
def post_chunk(pds_url: str, access_token: str, did: str, text: str, reply_to: Dict = None, embed: Dict = None, facets: List[Dict] = None) -> Tuple[str, str]:
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

    if facets:
        post["facets"] = facets

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

def post_thread(pds_url: str, handle: str, password: str, initial_text: str, long_text: str, image_path: str, alt_text: str, facets: List[Dict]):
    session = bsky_login_session(pds_url, handle, password)
    access_token = session["accessJwt"]
    did = session["did"]

    # Posta o primeiro texto com a imagem e facets
    embed = upload_image(pds_url, access_token, image_path, alt_text)
    uri, cid = post_chunk(pds_url, access_token, did, initial_text, embed=embed, facets=facets)

    # Posta o texto longo como uma thread
    chunks = split_text(long_text)
    reply_to = get_reply_refs(pds_url, uri)

    for chunk in chunks:
        uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to)
        reply_to = get_reply_refs(pds_url, uri)

    print("Thread postada com sucesso no Bluesky!")

pds_url = "https://bsky.social"
handle = BSKY_HANDLE
password = BSKY_PASSWORD
initial_text = mystring
long_text = explanation
image_path = image_path
alt_text = "Astronomy Picture of the Day"

resize_bluesky(image_path)
post_thread(pds_url, handle, password, initial_text, long_text, image_path, alt_text, facets)
