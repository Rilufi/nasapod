from instagrapi import Client
from instagrapi.exceptions import ClientError
from datetime import date, timezone, timedelta, datetime
import os

# Get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
hora = data_e_hora_sao_paulo.strftime('%H')

# What day is it?
today = date.today()
data = today.strftime("%d/%m")

# Authentication
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Defina as contas que você deseja monitorar
contas = [62183085222, 61863629167]

# Defina a palavra-chave que você deseja detectar
palavra_chave = data

# Crie uma instância do cliente Instagrapi
client = Client()

# Faça login na sua conta do Instagram
client.login(username, password)

# Para cada conta, verifique a última postagem
for conta in contas:
    # Obtenha a última postagem da conta
    postagem = client.user_medias(conta, 1)[0]

    # Verifique se a legenda da postagem contém a palavra-chave
    if palavra_chave in postagem["caption"]:
        # Se sim, compartilhe a postagem nos seus stories
        client.story_share(postagem["pk"])

# Aguarde alguns segundos para evitar problemas de taxa de limite
time.sleep(5)

# Logout da sua conta
client.logout()
