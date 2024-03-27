from instagrapi import Client
from instagrapi.exceptions import ClientError
from datetime import date, timezone, timedelta, datetime
import os

#get the time with timezone
fuso_horario = timezone(timedelta(hours=-3))
data_e_hora_atuais = datetime.now()
data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
hora = data_e_hora_sao_paulo.strftime('%H')

#what day is it?
today = date.today() # ex 2015-10-31
data = today.strftime("%d/%m")

# Autenticação
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Inicialize o cliente
client = Client()
client.login(username, password)  # Faça login na sua conta

# Contas que você deseja monitorar
contas = ["boturinsta", "doglufi"]

# Palavra específica na legenda
palavra_chave = data

# Verifique as últimas postagens de cada conta
for conta in contas:
    try:
        # Obtenha a última postagem da conta
        postagem = client.user_info_by_username(conta).latest_reel_media
        if postagem:
            # Verifique se a legenda contém a palavra-chave
            if palavra_chave in postagem.caption.text:
                # Compartilhe a postagem como história
                client.story_share(postagem.pk, "user")
                print(f"Postagem de {conta} compartilhada como história.")
            else:
                print(f"A última postagem de {conta} não contém a palavra-chave.")
        else:
            print(f"Nenhuma postagem encontrada para {conta}.")
    except ClientError as e:
        print(f"Erro ao obter postagem de {conta}: {e}")

# Logout
client.logout()
