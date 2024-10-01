import os
import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from atproto import Client

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

def load_interactions() -> Dict:
    """Loads interactions from a JSON file."""
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"O arquivo {INTERACTIONS_FILE} está vazio ou corrompido. Inicializando com valores padrão.")
                return {"likes": [], "reposts": [], "follows": []}
    return {"likes": [], "reposts": [], "follows": []}

def save_interactions(interactions: Dict):
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

def search_posts_by_hashtags(session: Client, hashtags: List[str], since: str, until: str) -> Dict:
    """Searches for posts containing the given hashtags within a specific time range."""
    hashtag_query = " OR ".join(hashtags)
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"Authorization": f"Bearer {session._access_jwt}"}
    params = {
        "q": hashtag_query,
        "limit": 100,
        "since": since,
        "until": until,
        "sort": "latest"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def find_images_with_keywords(post: Dict, keywords: List[str]) -> List[Dict]:
    """Finds images in the post with alt text containing any of the specified keywords."""
    images_with_keywords = []
    embed = post.get('record', {}).get('embed')

    if embed and embed.get('$type') == 'app.bsky.embed.images':
        images = embed.get('images', [])
        for image in images:
            alt_text = image.get('alt', '').lower()
            if any(keyword in alt_text for keyword in keywords):
                images_with_keywords.append(image)

    return images_with_keywords

def post_contains_hashtags(post: Dict, hashtags: List[str]) -> bool:
    """Verifica se o conteúdo do post contém alguma das hashtags especificadas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(hashtag.lower() in content for hashtag in hashtags)

def post_contains_ignored_hashtags(post: Dict, ignored_hashtags: List[str]) -> bool:
    """Verifica se o post contém hashtags que devem ser ignoradas."""
    content = post.get('record', {}).get('text', '').lower()
    return any(ignored_hashtag in content for ignored_hashtag in ignored_hashtags)

def like_post(client: Client, uri: str, cid: str, interactions: Dict):
    """Likes a post given its URI and CID, if not already liked."""
    if uri not in interactions["likes"]:
        client.like(uri=uri, cid=cid)
        interactions["likes"].append(uri)
        print(f"Post curtido: {uri}")

def repost_post(client: Client, uri: str, cid: str, interactions: Dict):
    """Reposts a post given its URI and CID, if not already reposted."""
    if uri not in interactions["reposts"]:
        client.repost(uri=uri, cid=cid)
        interactions["reposts"].append(uri)
        print(f"Post repostado: {uri}")

def follow_user(client: Client, did: str, interactions: Dict):
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

    # Define the hashtags and keywords to search for
    hashtags = [
        "#astronomy", "#space", "#universe", "#NASA", "#astrophysics",
        "#galaxy", "#astrophotography", "#hubble", "#universe",
        "#science", "#telescope", "#cosmology", "#nightsky", "#milkyway"
    ]
    keywords = ['space', 'astronomy', 'galaxy', 'nebula', 'moon', 'sun', 'star', 'stars', 'constellation', 'telescope', 'nightsky', 'sky', 'earth', 'planets', 'NASA']
    
    # Hashtags a serem ignoradas
    ignored_hashtags = ['#furry', '#furryart']

    # Calcula as datas de ontem e hoje no formato ISO com timezone-aware completo
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    since = yesterday.isoformat()  # YYYY-MM-DDTHH:MM:SS+00:00
    until = today.isoformat()      # YYYY-MM-DDTHH:MM:SS+00:00

    # Define the number of actions to perform per hour
    actions_per_hour = HOURLY_LIMIT
    action_counter = 0

    # Search for posts within the specified time range
    for hashtag in hashtags:
        try:
            search_results = search_posts_by_hashtags(client, [hashtag], since, until)
            
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

                    # Verifica se o post contém hashtags a serem ignoradas
                    if post_contains_ignored_hashtags(post, ignored_hashtags):
                        print(f"Post ignorado devido às hashtags: {uri}")
                        continue

                    # Verifica se a hashtag está presente no texto do post
                    if post_contains_hashtags(post, hashtags):
                        # Find images containing keywords in their alt descriptions
                        images = find_images_with_keywords(post, keywords)
                        
                        if images:
                            print(f"Post URI: {uri}")
                            print(f"Post CID: {cid}")
                            print(f"Author: {author_name}")
                            for image in images:
                                print(f"Image ALT: {image.get('alt', 'No ALT')}")
                                print(f"Image URL: {image.get('url', 'No URL')}")
                            print("-----\n")

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

            if action_counter >= actions_per_hour:
                break
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao buscar posts para {hashtag}: {e}")

    # Salva as interações para a próxima execução
    save_interactions(interactions)
    print("Concluído.")
