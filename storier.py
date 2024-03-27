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

# Initialize the client
client = Client()
client.login(username, password)

# Accounts to monitor
contas = ["boturinsta", "doglufi"]

# Specific word in the caption
palavra_chave = data

# Check the latest posts from each account
for conta in contas:
    try:
        # Get the user info by username
        user_info = client.user_info_by_username(conta)
        # Get the latest media from the user
        postagens = client.user_medias(user_id=user_info.pk, amount=1)
        if postagens:
            # Check if the caption contains the keyword
            caption = postagens[0].caption_text
            if palavra_chave in caption:
                # Like the story
                client.story_like(postagens[0].pk)
                print(f"Post from {conta} liked as story.")
            else:
                print(f"The latest post from {conta} does not contain the keyword.")
        else:
            print(f"No posts found for {conta}.")
    except ClientError as e:
        print(f"Error getting post from {conta}: {e}")

# Logout
client.logout()
