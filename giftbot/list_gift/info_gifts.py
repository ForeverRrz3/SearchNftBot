from aiogram.utils.formatting import TextLink
from requests import *
from bs4 import BeautifulSoup

def max_num_gift(name: str) -> int:
    url = f"https://t.me/nft/{name.replace(" ", "").replace("-","")}-1"
    response = get(url)

    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("div", class_="tgme_gift_table_wrap")

    max_number = data.find_all("td")[-1].text.strip().split("/")
    num = ""
    for i in max_number[0]:
        if i in "0123456789":
            num += i
    return int(num)



def get_all_models(name:str):
    url = f"https://fragment.com/gifts/{name.replace(" ", "").replace("-", "")}"
    response = get(url)

    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("div",
                     class_="tm-main-filters-box tm-main-filter-attr-model js-main-filters-box opened js-attribute")
    models = data.find_all("div", class_="tm-main-filters-item js-attribute-item")

    res = []
    for model in models:
        res.append(model.get("data-value"))
    return res


def get_all_symbol(name:str):

    url = f"https://t.me/nft/{name.replace(" ", "").replace("-", "")}-1"
    response = get(url)



def find_gift_info(name: str,num: int):
    res = {"Model": "", "Bg": "", "Symbol": ""}
    headers = {"User-Agent":
                   "mozilla/5.0 (Windows; U; Windows NT 6.1; en-Us; rv:1.9.1.5"}
    url = f"https://t.me/nft/{name.replace(" ", "").replace("-", "")}-{num}"
    response = get(url, headers=headers, timeout=10)

    soup = BeautifulSoup(response.text, "lxml")
    data_gift = soup.find_all("td")[:-1]

    Model = data_gift[1].text.strip().split()[:-1]
    res["Model"] = " ".join(Model)
    Bg = data_gift[2].text.strip().split()[:-1]
    res["Bg"] = " ".join(Bg)

    Symbol = data_gift[3].text.strip().split()[:-1]
    res["Symbol"] = " ".join(Symbol)

    return res