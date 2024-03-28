import os
from instapy import InstaPy


# Authentication
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Crie uma instância do InstaPy
session = InstaPy(username=username, password=password)

# Inicie a sessão
session.login()

# Defina as ações
session.like_by_tags(['astronomy', 'space'], amount=100)
session.set_do_follow(True, percentage=50)

# Finalize a sessão
session.end()
