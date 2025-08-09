import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from time import *

import requests
from database.models import Gift
from list_gift.info_gifts import max_num_gift
from sqlalchemy.ext.asyncio import AsyncSession
# res = {"Model": "", "Bg": "", "Symbol": ""}
# headers = {"User-Agent":
#                 "mozilla/5.0 (Windows; U; Windows NT 6.1; en-Us; rv:1.9.1.5"}
# url = f"https://t.me/nft/{name.replace(" ", "").replace("-", "")}-{num}"
# response = get(url, headers=headers, timeout=10)

# soup = BeautifulSoup(response.text, "lxml")
# data_gift = soup.find_all("td")[:-1]

# Model = data_gift[1].text.strip().split()[:-1]
# res["Model"] = " ".join(Model)
# Bg = data_gift[2].text.strip().split()[:-1]
# res["Bg"] = " ".join(Bg)

# Symbol = data_gift[3].text.strip().split()[:-1]
# res["Symbol"] = " ".join(Symbol)


import ssl


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
    
async def fetch_all_gifts(name_gift: str, session_db: AsyncSession) -> list:
    """Fetches all gifts for a given name."""
    semaphore = asyncio.Semaphore(30)
    max_gift_num = max_num_gift(name_gift)
    name_gift = name_gift.replace(' ', '').replace('-', '')

    async with ClientSession() as session:
        tasks = []

        for num_gift in range(max_gift_num, 0, -1):
            tasks.append(asyncio.create_task(fetch_gift_data(session, f"https://t.me/nft/{gift_name}-{i}", semaphore,session_db, name_gift, num_gift)))
        
        await asyncio.gather(*tasks)
        await session_db.commit()


async def fetch_gift_data(session: ClientSession, url: str, semaphore: asyncio.Semaphore, session_db: AsyncSession, name_gift: str, num_gift: int) -> dict:
    """Fetches a single gift's data."""
    headers = {"User-Agent":
                "mozilla/5.0 (Windows; U; Windows NT 6.1; en-Us; rv:1.9.1.5"}
    try:
        async with semaphore:
            async with session.get(url, ssl=ssl_context, headers=headers, timeout=10) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                data_gift = soup.find_all('td')[:-1]

                gift_data = {
                    'Model': ' '.join(data_gift[1].text.strip().split()[:-1]),
                    'Bg': ' '.join(data_gift[2].text.strip().split()[:-1]),
                    'Symbol': ' '.join(data_gift[3].text.strip().split()[:-1]),
                }
                session_db.add(Gift(name=name_gift, num=num_gift, model=gift_data['Model'], symbol=gift_data['Symbol'], bg=gift_data['Bg']))
                return gift_data
    except IndexError:
        return None
    except Exception as e:
        asyncio.sleep(10)
        fetch_gift_data(session, url, semaphore, session_db, name_gift, num_gift)


def find_gift_info(name: str,num: int):
    try:
        res = {"Model": "", "Bg": "", "Symbol": ""}
        headers = {"User-Agent":
                    "mozilla/5.0 (Windows; U; Windows NT 6.1; en-Us; rv:1.9.1.5"}
        url = f"https://t.me/nft/{name.replace(" ", "").replace("-", "")}-{num}"
        response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "lxml")
        data_gift = soup.find_all("td")[:-1]

        Model = data_gift[1].text.strip().split()[:-1]
        res["Model"] = " ".join(Model)
        Bg = data_gift[2].text.strip().split()[:-1]
        res["Bg"] = " ".join(Bg)

        Symbol = data_gift[3].text.strip().split()[:-1]
        res["Symbol"] = " ".join(Symbol)

        return res
    except Exception as e:
        sleep(5)
        print(e)


def get_all(name):
    for i in range(2000, 0, -1):
        find_gift_info(name,i)

st = time()
a = asyncio.run(fetch_all_gifts('PlushPepe'))
print(time() - st)
st = time()
get_all('PlushPepe')
print(time() - st)
