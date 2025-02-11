import os
from typing import Dict, List
import requests
from atproto import Client
from datetime import datetime, timedelta, timezone
import time

# Configurações do Bluesky
BSKY_HANDLE = os.environ.get("BSKY_HANDLE")  # Handle do Bluesky
BSKY_PASSWORD = os.environ.get("BSKY_PASSWORD")  # Senha do Bluesky
PDS_URL = "https://bsky.social"  # URL do Bluesky
BOT_NAME = "Apodsky"  # Nome do bot para evitar interagir com os próprios posts

# Configurações do GitHub
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Token de acesso do GitHub
GITHUB_REPO = "Rilufi/nasapod"  # Substitua pelo seu usuário/repositório
GITHUB_FILE_PATH = "interactions.txt"  # Caminho do arquivo no repositório

# Limites diários e ações permitidas por hora
DAILY_LIMIT = 11666  # Limite de ações diárias
HOURLY_LIMIT = DAILY_LIMIT // 24  # Limite de ações por hora

def load_interactions():
    """Carrega interações do arquivo interactions.txt no GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content = response.json().get("content", "")
        if content:
            # Decodifica o conteúdo (base64) e divide em linhas
            import base64
            decoded_content = base64.b64decode(content).decode("utf-8")
            return decoded_content.splitlines()
    elif response.status_code == 404:
        print(f"Arquivo {GITHUB_FILE_PATH} não encontrado no repositório. Inicializando com lista vazia.")
    else:
        print(f"Erro ao carregar interações: {response.status_code} - {response.text}")
    
    return []

def save_interactions(interactions):
    """Salva interações no arquivo interactions.txt no GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Obtém o SHA do arquivo atual (necessário para atualização)
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None
    
    # Converte a lista de interações em uma string
    content = "\n".join(interactions)
    
    # Codifica o conteúdo em base64
    import base64
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # Envia a requisição para atualizar o arquivo
    data = {
        "message": "Atualizando interações",
        "content": encoded_content,
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Interações salvas no GitHub: {GITHUB_FILE_PATH}")
    else:
        print(f"Erro ao salvar interações: {response.status_code} - {response.text}")

def bsky_login_session(pds_url: str, handle: str, password: str) -> Client:
    """Autentica no Bluesky e retorna a instância do cliente."""
    print("Tentando autenticar no Bluesky...")
    client = Client(base_url=pds_url)
    client.login(handle, password)
    print("Autenticação bem-sucedida.")
    return client

def check_rate_limit(response):
    """Verifica o status do limite de requisições e pausa, se necessário."""
    rate_limit_remaining = int(response.headers.get('RateLimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('RateLimit-Reset', 0))

    if rate_limit_remaining <= 1:
        reset_time = datetime.fromtimestamp(rate_limit_reset, timezone.utc)
        current_time = datetime.now(timezone.utc)
        wait_seconds = (reset_time - current_time).total_seconds()
        if wait_seconds > 0:
            print(f"Limite de requisições atingido. Aguardando {wait_seconds:.0f} segundos para o reset.")
            time.sleep(wait_seconds)
        else:
            print("Limite de requisições atingido, mas o tempo de reset já passou.")

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(hashtag.lower() in content for hashtag in hashtags)

def search_posts_by_hashtags(session: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Busca posts contendo as hashtags fornecidas dentro de um intervalo de tempo."""
    cleaned_hashtags = [hashtag.replace('#', '').lower() for hashtag in hashtags]
    hashtag_query = " OR ".join(cleaned_hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    
    # Obtém o token de acesso da sessão
    access_jwt = session._session.access_jwt  # Corrigido aqui
    headers = {"Authorization": f"Bearer {access_jwt}"}
    
    params = {
        "q": hashtag_query,
        "limit": 50,
        "since": since,
        "until": until,
        "sort": "latest"
    }

    response = requests.get(url, headers=headers, params=params)
    check_rate_limit(response)  # Verifica e gerencia o limite de requisições

    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Erro ao buscar posts para {hashtag_query}: {e}")
        print(f"Detalhes do erro: {response.text}")
        return {}

def like_post_bluesky(client: Client, uri: str, cid: str, interactions):
    """Curtir um post no Bluesky."""
    if f"like:{uri}" not in interactions:
        client.like(uri=uri, cid=cid)
        interactions.append(f"like:{uri}")
        save_interactions(interactions)  # Salva as interações após cada like
        print(f"Post curtido no Bluesky: {uri}")
    else:
        print(f"Post já curtido anteriormente: {uri}")

def repost_post_bluesky(client: Client, uri: str, cid: str, interactions):
    """Repostar um post no Bluesky."""
    if f"repost:{uri}" not in interactions:
        client.repost(uri=uri, cid=cid)
        interactions.append(f"repost:{uri}")
        save_interactions(interactions)  # Salva as interações após cada repost
        print(f"Post repostado no Bluesky: {uri}")
    else:
        print(f"Post já repostado anteriormente: {uri}")

if __name__ == "__main__":
    interactions = load_interactions()
    bsky_client = bsky_login_session(PDS_URL, BSKY_HANDLE, BSKY_PASSWORD)

    # Define hashtags e palavras-chave para busca
    hashtags = [
        "#astrophysics", "#galaxy", "#astrophotography", "#hubble", "#universe",
        "#science", "#telescope", "#cosmology", "#nightsky", "#milkyway"
    ]

    # Calcula as datas de ontem e hoje no formato ISO com timezone-aware completo
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()  # YYYY-MM-DDTHH:MM:SS+00:00
    until = today.isoformat()      # YYYY-MM-DDTHH:MM:SS+00:00

    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Interação no Bluesky
    for hashtag in hashtags:
        try:
            search_results = search_posts_by_hashtags(bsky_client, [hashtag], since, until)
            if not search_results.get('posts'):
                print(f"Nenhum resultado encontrado para {hashtag} no Bluesky.")
            else:
                for post in search_results["posts"]:
                    uri = post.get('uri')
                    cid = post.get('cid')
                    author = post.get('author', {})

                    # Evita interagir com posts do próprio bot
                    if author.get('displayName', '') == BOT_NAME:
                        continue

                    if post_contains_hashtags(post, [hashtag]):
                        if action_counter < actions_per_hour:
                            like_post_bluesky(bsky_client, uri, cid, interactions)
                            repost_post_bluesky(bsky_client, uri, cid, interactions)
                            action_counter += 2  # Conta como duas ações (like e repost)

                    if action_counter >= actions_per_hour:
                        print("Limite de ações por hora atingido no Bluesky.")
                        break
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao buscar posts para {hashtag} no Bluesky: {e}")

    print("Concluído.")
