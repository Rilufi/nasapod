import os
from instapy import InstaPy
from selenium import webdriver

# Authentication (using environment variables)
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# WebDriver path (replace with the actual path)
#driver_path = "/path/to/geckodriver"

# Define options for headless mode (if needed)
options = webdriver.FirefoxOptions()
options.add_argument("--headless")  # Uncomment for headless mode

# Create a session with explicit driver path
session = InstaPy(username=username, password=password, webdriver_options=options)

# Inicie a sessão
session.login()

# Defina as ações
session.like_by_tags(['astronomy', 'space'], amount=100)
session.set_do_follow(True, percentage=50)

# Finalize a sessão
session.end()
