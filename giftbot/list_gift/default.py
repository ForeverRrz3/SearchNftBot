from bs4 import BeautifulSoup
from requests import *
from inflect import *

def find_all_gifts():
    gifts = []
    url = "https://fragment.com/gifts"
    response = get(url)

    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("div", class_="tm-main-catalog-filters")
    data_gifts = data.find_all("a", class_="tm-main-filters-item js-choose-collection-item")

    for gift in data_gifts:
        gifts.append(engine().singular_noun(gift.text.strip().split("\n")[0]))

    return gifts



def get_name(base_name: str):
    url = f"https://t.me/nft/{base_name}-1"
    response = get(url)

    soup = BeautifulSoup(response.text,"lxml")
    data = soup.find("div",class_="tgme_page tgme_page_gift")
    g = data.find_all("g")[-1]
    return g.text.strip().split("\n")[0]
