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

# Para cada conta, verifique a última postagem
for conta in contas:
    # Obtenha a última postagem da conta
    postagem = client.user_medias(conta, 1)[0]

    if palavra_chave in postagem.caption_text:
        # Create a custom story with a placeholder image
        client.story_configure(
            background_color="F5F8FA",
            media_type=instagrapi.MediaType.PHOTO,
            media_file="placeholder.jpg"  # Replace with a placeholder image
         )

    # Overlay the post's media on top of the custom story
    # (Adjust coordinates as needed)
        client.story_add_sticker(
            sticker_type=instagrapi.StorySticker.PHOTO,
            x=0.5,
            y=0.5,
            media=postagem.media_file  # Assuming postagem contains the post's media
    )

        # Publish the story
        client.story_publish()

# Aguarde alguns segundos para evitar problemas de taxa de limite
time.sleep(5)

# Logout da sua conta
client.logout()
