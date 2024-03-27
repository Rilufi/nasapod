from instapy import InstaPy
import os

# Authentication
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

session = InstaPy(username=username, password=password)
session.login()
session.like_by_tags(["astronomy"], amount=10)
session.set_do_follow(True, percentage=100)
session.end()
