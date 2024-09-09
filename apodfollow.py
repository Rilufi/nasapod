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
from PIL import Image


# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Apodbot"  # Nome do bot para evitar interagir com os próprios posts

# Limites diários e ações permitidas por hora
DAILY_LIMIT = 11666  # Limite de ações diárias
HOURLY_LIMIT = DAILY_LIMIT // 24  # Limite de ações por hora

# Arquivo para armazenar interações
INTERACTIONS_FILE = 'interactions.json'

def load_interactions():
    """Loads interactions from a JSON file."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # O arquivo está vazio ou corrompido; inicializar com valores padrão
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "reposts": [], "follows": []}
    # Se o arquivo não existir, retorna interações padrão
    return {"likes": [], "reposts": [], "follows": []}


def save_interactions(interactions):
    """Saves interactions to a JSON file."""
    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(interactions, file)

def bsky_login_session(pds_url: str, handle: str, password: str) -> Client:
    """Logs in to Bluesky and returns the client instance."""
    print("Tentando autenticar no Bluesky...")
    client = Client(base_url=pds_url)
    client.login(handle, password)
    print("Autenticação bem-sucedida.")
    return client

def search_posts_by_hashtags(session: Client, hashtags: List[str]) -> Dict:
    """Searches for posts containing the given hashtags."""
    hashtag_query = " OR ".join(hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session._access_jwt}"}  # Usando _access_jwt obtido do client
    params = {"q": hashtag_query, "limit": 50}  # Ajuste o limite conforme necessário

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def like_post(client: Client, uri: str, cid: str, interactions):
    """Likes a post given its URI and CID, if not already liked."""
    if uri not in interactions["likes"]:
        client.like(uri=uri, cid=cid)
        interactions["likes"].append(uri)
        print(f"Post curtido: {uri}")

def repost_post(client: Client, uri: str, cid: str, interactions):
    """Reposts a post given its URI and CID, if not already reposted."""
    if uri not in interactions["reposts"]:
        client.repost(uri=uri, cid=cid)
        interactions["reposts"].append(uri)
        print(f"Post repostado: {uri}")

def follow_user(client: Client, did: str, interactions):
    """Follows a user given their DID, if not already followed."""
    if did not in interactions["follows"]:
        client.follow(did)
        interactions["follows"].append(did)
        print(f"Seguindo usuário: {did}")

if __name__ == "__main__":
    # Carrega interações passadas para evitar duplicatas
    interactions = load_interactions()

    # Login to Bluesky
    client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define the hashtags to search for
    hashtags = [
      "#astronomy",
      "#space",
      "#universe",
      "#NASA",
      "#cosmos",
      "#galaxy",
      "#astrophotography",
      "#science",
      "#telescope",
      "#cosmology"
  ]

    # Define the number of actions to perform per hour
    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Search for posts
    for hashtag in hashtags:
        search_results = search_posts_by_hashtags(client, [hashtag])
        
        # Print detailed information about the search results
        print(f"Resultados da pesquisa para {hashtag}:")
        if not search_results.get('posts'):
            print("Nenhum resultado encontrado.")
        else:
            for post in search_results["posts"]:
                uri = post.get('uri')
                cid = post.get('cid')
                author = post.get('author', {})
                author_name = author.get('displayName', 'Unknown')
                author_did = author.get('did', '')

                # Evitar interagir com posts do próprio bot
                if author_name == BOT_NAME:
                    continue

                # Curtir, repostar e seguir o autor do post se ainda não interagido
                if action_counter < actions_per_hour:
                    like_post(client, uri, cid, interactions)
                    action_counter += 1
                if action_counter < actions_per_hour:
                    repost_post(client, uri, cid, interactions)
                    action_counter += 1
                if action_counter < actions_per_hour:
                    follow_user(client, author_did, interactions)
                    action_counter += 1

                # Verifica se o limite de ações foi atingido
                if action_counter >= actions_per_hour:
                    print("Limite de ações por hora atingido.")
                    break

    # Salva as interações para a próxima execução
    save_interactions(interactions)
