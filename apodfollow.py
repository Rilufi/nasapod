import os
import json
from datetime import datetime, timezone
from typing import Dict, List
from atproto import Client, firehose

# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Apodbot"  # Nome do bot para evitar interagir com os próprios posts

# Arquivo para armazenar interações
INTERACTIONS_FILE = 'interactions.json'

def load_interactions() -> Dict:
    """Carrega interações de um arquivo JSON."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "reposts": [], "follows": []}
    return {"likes": [], "reposts": [], "follows": []}

def save_interactions(interactions: Dict):
    """Salva interações em um arquivo JSON."""
    with open(INTERACTIONS_FILE, 'w') as file:
        json.dump(interactions, file)

def bsky_login_session(pds_url: str, handle: str, password: str) -> Client:
    """Autentica no Bluesky e retorna a instância do cliente."""
    print("Tentando autenticar no Bluesky...")
    client = Client(base_url=pds_url)
    client.login(handle, password)
    print("Autenticação bem-sucedida.")
    return client

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(hashtag.lower() in content for hashtag in hashtags)

def post_contains_ignored_hashtags(post: Dict, ignored_hashtags: List[str]) -> bool:
    """Verifica se o post contém hashtags que devem ser ignoradas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(ignored_hashtag in content for ignored_hashtag in ignored_hashtags)

def like_post(client: Client, uri: str, cid: str, interactions: Dict):
    """Curtir um post, dado seu URI e CID, se ainda não curtido."""
    if uri not in interactions["likes"]:
        client.like(uri=uri, cid=cid)
        interactions["likes"].append(uri)
        print(f"Post curtido: {uri}")

def follow_user(client: Client, did: str, interactions: Dict):
    """Seguir um usuário, dado seu DID, se ainda não seguido."""
    if did not in interactions["follows"]:
        client.follow(did)
        interactions["follows"].append(did)
        print(f"Seguindo usuário: {did}")

if __name__ == "__main__":
    # Carrega interações passadas para evitar duplicatas
    interactions = load_interactions()

    # Login no Bluesky
    client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define as hashtags e palavras-chave para busca
    hashtags = [
        "#astronomy", "#space", "#universe", "#NASA", "#astrophysics",
        "#galaxy", "#astrophotography", "#hubble", "#universe",
        "#science", "#telescope", "#cosmology", "#nightsky", "#milkyway"
    ]
    
    # Hashtags a serem ignoradas
    ignored_hashtags = ['#furry', '#furryart']

    # Conecta ao Firehose
    print("Conectando ao Firehose...")
    for message in firehose.connect():
        if message.type == "post":
            post = message.record
            author = message.author
            uri = message.uri
            cid = message.cid

            # Verifica se o post contém hashtags a serem ignoradas
            if post_contains_ignored_hashtags(post, ignored_hashtags):
                print(f"Post ignorado devido às hashtags: {uri}")
                continue

            # Verifica se a hashtag está presente no texto do post
            if post_contains_hashtags(post, hashtags):
                print(f"Novo post encontrado: {uri}")
                print(f"Conteúdo: {post.get('record', {}).get('text', '')}")
                print(f"Autor: {author.get('displayName', 'Unknown')}")

                # Curtir e seguir o autor do post
                like_post(client, uri, cid, interactions)
                follow_user(client, author.get('did', ''), interactions)

    # Salva as interações para a próxima execução
    save_interactions(interactions)
    print("Concluído.")
