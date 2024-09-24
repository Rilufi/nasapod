#!/usr/bin/env python
# coding=utf-8

import os
import sys
import random
import urllib.request
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
from PIL import Image
import google.generativeai as genai
import time

# Inicializando o cliente do Bluesky e Google
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
API_KEY = os.environ.get("API_KEY")
MODEL = genai.GenerativeModel('gemini-1.5-flash')

# Configurações do Bluesky
PDS_URL = "https://bsky.social"

# Função para implementar retry com backoff exponencial
def retry_request(func, *args, retries=5, backoff_factor=1, **kwargs):
    for attempt in range(retries):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            wait = backoff_factor * (2 ** attempt)
            print(f"Erro: {e}. Retentando em {wait} segundos...")
            time.sleep(wait)
    print("Todas as tentativas falharam.")
    sys.exit(1)

# Função para obter o fuso horário e a hora atual em SP
def obter_hora_sao_paulo() -> str:
    fuso_horario = timezone(timedelta(hours=-3))
    data_e_hora_sao_paulo = datetime.now().astimezone(fuso_horario)
    hora = data_e_hora_sao_paulo.strftime('%H')
    return hora

# Função para gerar uma data aleatória entre 16 de junho de 1995 e ontem
def gerar_data_aleatoria() -> str:
    data_inicial = datetime(1995, 6, 16)
    ontem = datetime.now() - timedelta(days=1)
    dias_entre_datas = (ontem - data_inicial).days
    dias_aleatorios = random.randrange(dias_entre_datas)
    data_aleatoria = data_inicial + timedelta(days=dias_aleatorios)
    return data_aleatoria.strftime("%Y-%m-%d")

# Função para formatar a data em dois formatos
def formatar_data(data_str: str) -> Tuple[str, str]:
    data = datetime.strptime(data_str, "%Y-%m-%d")
    formato1 = data.strftime("%Y-%m-%d")
    formato2 = data.strftime("%y%m%d")
    return formato1, formato2

# Função para criar facets de link
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

# Função para encontrar hashtags e criar facets
def find_hashtags(text: str) -> List[Dict]:
    facets = []
    words = text.split()
    byte_index = 0

    for word in words:
        if word.startswith("#"):
            start = byte_index
            end = byte_index + len(word)
            facets.append({
                "index": {
                    "byteStart": start,
                    "byteEnd": end
                },
                "features": [{
                    "$type": "app.bsky.richtext.facet#tag",
                    "tag": word[1:]  # Remove o '#' para a tag
                }]
            })
        byte_index += len(word) + 1  # +1 para o espaço após a palavra

    return facets

# Função para gerar hashtags e alt_text usando Gemini
def gemini_image(prompt: str, image_path: str) -> Tuple[str, str]:
    try:
        # Carregando a imagem
        imagem = Image.open(image_path)
        if imagem.mode == 'P':
            imagem = imagem.convert('RGB')

        # Gerando conteúdo com base na imagem e no prompt
        response = MODEL.generate_content([prompt, imagem], stream=True)

        # Aguarda a conclusão da iteração antes de acessar os candidatos
        response.resolve()

        # Verificando a resposta
        if response.candidates and len(response.candidates) > 0:
            if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
                text = response.candidates[0].content.parts[0].text

                # Supondo que o alt-text esteja separado por "ALT-TEXT:" na resposta
                if "ALT-TEXT:" in text:
                    parts = text.split("ALT-TEXT:")
                    hashtags = parts[0].strip()
                    alt_text = parts[1].strip()
                    return hashtags, alt_text
        print("Nenhum candidato válido encontrado pelo Gemini.")
        return "", ""
    except Exception as e:
        print(f"Erro ao gerar hashtags e alt_text com Gemini: {e}")
        return "", ""

# Função para redimensionar a imagem para Bluesky
def resize_bluesky(image_path: str, max_file_size: int = 1 * 1024 * 1024) -> None:
    try:
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
    except Exception as e:
        print(f"Erro ao redimensionar a imagem: {e}")

# Função para criar sessão de login no Bluesky
def bsky_login_session(pds_url: str, handle: str, password: str) -> Dict:
    try:
        resp = retry_request(
            requests.post,
            pds_url + "/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password}
        )
        return resp.json()
    except Exception as e:
        print(f"Erro ao criar sessão no Bluesky: {e}")
        sys.exit(1)

# Função para fazer upload de arquivo no Bluesky
def upload_file(pds_url: str, access_token: str, filename: str, img_bytes: bytes) -> str:
    try:
        suffix = filename.split(".")[-1].lower()
        mimetype = "application/octet-stream"
        if suffix == "png":
            mimetype = "image/png"
        elif suffix in ["jpeg", "jpg"]:
            mimetype = "image/jpeg"
        elif suffix == "webp":
            mimetype = "image/webp"

        resp = retry_request(
            requests.post,
            pds_url + "/xrpc/com.atproto.repo.uploadBlob",
            headers={
                "Content-Type": mimetype,
                "Authorization": f"Bearer {access_token}",
            },
            data=img_bytes,
        )
        return resp.json()["blob"]
    except Exception as e:
        print(f"Erro ao fazer upload do arquivo: {e}")
        sys.exit(1)

# Função para fazer upload de imagem no Bluesky
def upload_image(pds_url: str, access_token: str, image_path: str, alt_text: str) -> Dict:
    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()

        if len(img_bytes) > 1000000:
            raise Exception(f"Imagem muito grande. Máximo permitido é 1000000 bytes, obtido: {len(img_bytes)}")

        blob = upload_file(pds_url, access_token, image_path, img_bytes)
        return {
            "$type": "app.bsky.embed.images",
            "images": [{"alt": alt_text or "", "image": blob}],
        }
    except Exception as e:
        print(f"Erro ao fazer upload da imagem: {e}")
        sys.exit(1)

# Função para dividir texto em chunks
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

# Função para criar facets de link
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

# Função para criar facets de reply (respostas)
def get_reply_refs(pds_url: str, parent_uri: str) -> Dict:
    try:
        repo, collection, rkey = parent_uri.split("/")[2:5]
        resp = retry_request(
            requests.get,
            pds_url + "/xrpc/com.atproto.repo.getRecord",
            params={"repo": repo, "collection": collection, "rkey": rkey},
        )
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
    except Exception as e:
        print(f"Erro ao obter referências de reply: {e}")
        sys.exit(1)

# Função para postar um chunk no Bluesky
def post_chunk(pds_url: str, access_token: str, did: str, text: str, reply_to: Dict = None, embed: Dict = None, facets: List[Dict] = None) -> Tuple[str, str]:
    try:
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

        resp = retry_request(
            requests.post,
            pds_url + "/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "repo": did,
                "collection": "app.bsky.feed.post",
                "record": post,
            },
        )

        response_data = resp.json()
        return response_data["uri"], response_data["cid"]
    except Exception as e:
        print(f"Erro ao postar chunk: {e}")
        sys.exit(1)

# Função para postar a thread completa no Bluesky
def post_thread(pds_url: str, handle: str, password: str, initial_text: str, long_text: str, image_path: str, alt_text: str, facets: List[Dict]):
    try:
        session = bsky_login_session(pds_url, handle, password)
        access_token = session["accessJwt"]
        did = session["did"]

        # Fazer upload da imagem
        embed = upload_image(pds_url, access_token, image_path, alt_text)

        # Postar o primeiro chunk com a imagem e facets
        uri, cid = post_chunk(pds_url, access_token, did, initial_text, embed=embed, facets=facets)

        # Postar o texto longo como uma thread
        chunks = split_text(long_text)
        reply_to = get_reply_refs(pds_url, uri)

        for chunk in chunks:
            uri, cid = post_chunk(pds_url, access_token, did, chunk, reply_to=reply_to)
            reply_to = get_reply_refs(pds_url, uri)

        print("Thread postada com sucesso no Bluesky!")
    except Exception as e:
        print(f"Erro ao postar thread: {e}")
        sys.exit(1)

# Função principal
def main():
    hora = obter_hora_sao_paulo()

    if hora == '07':
        data = datetime.now().strftime("%Y-%m-%d")
        iniciar_com = "Astronomy Picture of the Day"

        # Formato especial para o horário das 7, sem a inclusão da data no request da API
        URL_APOD = "https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': API_KEY,
            'hd': 'True',
            'thumbs': 'True',
        }

        response = retry_request(requests.get, URL_APOD, params=params)
        apod_data = response.json()

        # Se 'count' estiver presente, a resposta será uma lista
        if isinstance(apod_data, list):
            apod_data = apod_data[0]

        url = apod_data.get('url')
        thumbs = apod_data.get('thumbnail_url')
        media_type = apod_data.get('media_type')
        explanation = apod_data.get('explanation')
        title = apod_data.get('title')

        # Usar o site com a data atual no formato específico
        formato2 = datetime.now().strftime("%y%m%d")
        site = f"https://apod.nasa.gov/apod/ap{formato2}.html"

    else:
        data = gerar_data_aleatoria()
        iniciar_com = ""  # Iniciar diretamente com o título

        formato1, formato2 = formatar_data(data)

        # Buscar APOD para outras horas que não sejam 07
        URL_APOD = "https://api.nasa.gov/planetary/apod"
        params = {
            'api_key': API_KEY,
            'hd': 'True',
            'thumbs': 'True',
            'date': formato1
        }

        response = retry_request(requests.get, URL_APOD, params=params)
        apod_data = response.json()

        url = apod_data.get('url')
        thumbs = apod_data.get('thumbnail_url')
        media_type = apod_data.get('media_type')
        explanation = apod_data.get('explanation')
        title = apod_data.get('title')

        # Definir o site com base na data formatada
        site = f"https://apod.nasa.gov/apod/ap{formato2}.html"

    # Criar o texto inicial "Astronomy Picture of the Day"
    if iniciar_com:
        mystring = f"""Astronomy Picture of the Day

Title: {title}

Source: {site}
"""
    else:
        mystring = f"""{title}

Source: {site}
"""


    # Recuperar a imagem ou thumbnail
    if media_type == 'image':
        image_url = url
    elif media_type == 'video':
        image_url = thumbs
    else:
        print("Tipo de mídia não suportado.")
        sys.exit(1)

    # Baixar a imagem
    try:
        urllib.request.urlretrieve(image_url, 'apodtoday.jpeg')
        print(f"Imagem baixada: {image_url}")
    except Exception as e:
        print(f"Erro ao baixar a imagem: {e}")
        sys.exit(1)

    # Gerar hashtags e alt_text usando Gemini
    prompt = f"Based on the following explanation and image, create engaging astronomy related hashtags and a descriptive alt text. Separate the hashtags from the alt text with 'ALT-TEXT:'.\n\nExplanation: {explanation}"
    hashtags, alt_text = gemini_image(prompt, 'apodtoday.jpeg')

    # Atualizar o texto completo com ou sem hashtags, dependendo do horário
    if iniciar_com:
        # Postagem das 11h não incluirá hashtags
        full_text = mystring
    else:
        # Postagens em outros horários incluirão hashtags
        full_text = f"""{mystring}
    
    {hashtags}"""

    # Criar facets para hashtags
    hashtag_facets = find_hashtags(full_text)

    # Criar facets para o link
    link_facets = create_link_facets(full_text, site, site)

    # Combinar todas as facets
    all_facets = hashtag_facets + link_facets
    
    # Redimensionar a imagem se necessário
    resize_bluesky('apodtoday.jpeg')

    # Postar no Bluesky
    post_thread(
        pds_url=PDS_URL,
        handle=BSKY_HANDLE,
        password=BSKY_PASSWORD,
        initial_text=full_text,
        long_text=explanation,
        image_path='apodtoday.jpeg',
        alt_text=alt_text,
        facets=all_facets
    )

if __name__ == "__main__":
    main()
