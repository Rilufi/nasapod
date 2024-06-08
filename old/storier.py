import os
from instapy import InstaPy


# Authentication (using environment variables)
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# Create a session (headless mode needs InstaPy v0.7.0 or above)
session = InstaPy(username=username, password=password, headless_browser=True)

# Inicie a sessão
session.login()

# Defina as ações
session.like_by_tags(['astronomy', 'space'], amount=100)
session.set_do_follow(True, percentage=50)

# Finalize a sessão
session.end()
