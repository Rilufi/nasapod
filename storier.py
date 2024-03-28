from instagrapi import Client
from instagrapi.exceptions import ClientError
import time
import os

# Authentication
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Inicialize o cliente
client = Client()
client.login(username, password)  # Faça login na sua conta

# ID da conta oficial da NASA no Instagram
nasa_user_id = "1518284433"  # ID da conta oficial da NASA

# Obtenha os seguidores da conta oficial da NASA
try:
    followers = client.user_followers(nasa_user_id, amount=50)  # Obtenha 50 seguidores da NASA
    for follower in followers:
        # Siga o seguidor
        client.user_follow(follower.pk)
        print(f"Seguindo {follower.username}")
        time.sleep(360)  # Espere 6 minutos antes de seguir o próximo seguidor (50 seguidores em 5 horas)
except ClientError as e:
    print(f"Erro ao obter seguidores da NASA: {e}")

# Logout
client.logout()
