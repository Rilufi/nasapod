import os
from threadspy import ThreadsAPI


username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
api = ThreadsAPI(username=username, password=password)
api.publish(caption="Primeiro teste funcionou, yay. Testando agora a automação (se esse for, o próximo teste já vai ser os rolê da nasa)")
