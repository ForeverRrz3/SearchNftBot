from requests import *
from bs4 import BeautifulSoup

def is_valid(username: str):
    url = "https://t.me/"+username[1:]
    response = get(url)
    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("a", class_="tgme_action_button_new shine")
    if data is None:
        return False
    return True
