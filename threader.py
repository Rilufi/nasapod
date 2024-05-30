import os
from threadspy import ThreadsAPI


username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
api = ThreadsAPI(username="username", password="password")
api.publish(caption="Testando. Se você estiver vendo isso daqui quer dizer que funcionou")
