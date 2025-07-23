from aiogram.utils.formatting import TextLink
from requests import *
from bs4 import BeautifulSoup
from sqlalchemy.util import await_only

from list_gift.info_gifts import max_num_gift
from inflect import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

def next_find_gift(name:str ,num:int, data: dict):

    list_gift = []

    for i in ["Model","Back","Symbol"]:
        data.setdefault(i,"all")
    data.setdefault("Desc",False)

    cnt = 0
    while cnt <20 :
        if num <= 0:
            break
        res = find_gift_info(name,num)
        print(res)
        if (res["Model"] in data["Model"] or data["Model"] == "all") and (res["Back"] in data["Back"] or data["Back"] == "all") and \
                (res["Symbol"] in data["Symbol"] or data["Symbol"] == "all"):
            cnt +=1
            list_gift.append(TextLink(
                name+"  "+"#"+str(num),
                url=f"https://t.me/nft/{name.replace(" ","").replace("-","")}-{num}") + "\n")
        num-=1
    print(list_gift)
    return list_gift, num


def last_find_gift(name:str, num:int):

    list_gift = []
    max_num = max_num_gift(name)

    for i in range(num+40,num+20,-1):
        if max_num < num:
            break
        list_gift.append(TextLink(
            name+"  "+"#"+str(i),
            url=f"https://t.me/nft/{name.replace(" ","").replace("-","")}-{i}") + "\n")


    return list_gift, i



def is_ok_gift(name: str, num: int):

    url = f"https://fragment.com/gift/{name.replace(" ","").replace("-","")}-{num}"
    response = get(url)

    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find("span", class_="tm-section-header-domain")
    if data == None:
        return False

    return True






def find_gift_info(name: str,num: int):
    res = {"Model": "", "Bg": "", "Symbol": ""}
    url = f"https://t.me/nft/{name.replace(" ", "").replace("-", "")}-{num}"
    response = get(url)

    soup = BeautifulSoup(response.text, "lxml")

    data_gift = soup.find_all("td")[:-1]
    print(data_gift)

    Model = data_gift[1].text.strip().split()[:-1]
    res["Model"] = " ".join(Model)

    Bg = data_gift[2].text.strip().split()[:-1]
    res["Bg"] = " ".join(Bg)

    Symbol = data_gift[3].text.strip().split()[:-1]
    res["Symbol"] = " ".join(Symbol)

    return res
