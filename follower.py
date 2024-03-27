from instagrapi import Client
import time
import random
import os
import requests

# Chamando variáveis secretas
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Criando um cliente instagrapi
client = Client(request_timeout=7)
client.login(username, password)

# Definindo o usuário alvo ou hashtag relacionada à astronomia
target_hashtag = "#astronomy"

# Definindo o número total de contas seguidas
total_followed = 0

# Set the custom user agent in the headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

while total_followed < 30:
    # Pesquisando por postagens relacionadas à hashtag de astronomia
    response = requests.get(
        f"https://www.instagram.com/explore/tags/{target_hashtag}/?__a=1",
        headers=headers
    )
    if response.status_code == 200:
        try:
            json_data = response.json()
            results = json_data.get('graphql', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
        except ValueError:
            print("Failed to decode JSON from response")
            break
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        break
    
    # Extrair os IDs dos usuários das postagens encontradas
    user_ids = [result['node']['owner']['id'] for result in results]
    
    # Iterar sobre os IDs dos usuários encontrados e segui-los
    for user_id in user_ids:
        client.user_follow(user_id)
        total_followed += 1
        print(f"Followed user {total_followed}/{30}")
        if total_followed >= 30:
            break  # Parar se o limite de 30 contas seguidas for atingido
        time.sleep(360)  # Esperar 6 minutos antes de seguir a próxima conta

# Fazer logout após completar as ações
client.logout()
