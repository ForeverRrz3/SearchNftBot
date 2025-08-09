import asyncio



from aiogram.utils.formatting import TextLink, as_marked_list, as_list, as_marked_section
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from requests import *
from bs4 import BeautifulSoup

from database.models import Gift, Banner, NameGift, Symbol, Bg, Admins
from sqlalchemy import select,update,delete, values

from list_gift.default import find_all_gifts

from list_gift.find_gifts import max_num_gift
from list_gift.info_gifts import find_gift_info


import ssl

async def orm_get_all_gifts(session:AsyncSession, name: str):

    num = max_num_gift(name)
    print(5345432)
    for i in range(num, 0, -1):
        print(i)
        res = find_gift_info(name,i)
        obj = Gift(
            name=name,
            num=i,
            model=res["Model"],
            bg=res["Bg"],
            symbol=res["Symbol"]
        )
        session.add(obj)
    await session.commit()

################## Создание/получение баннеров ###########################

async def orm_create_banners(session: AsyncSession, banners: dict):
    query = select(Banner)
    result = await session.execute(query)
    res = result.scalars().all()
    if result.first() and len(res) == len(banners.values()):
        return

    in_bd = [banner.name for banner in res]
    session.add_all([Banner(name=name, description=description) for name, description in banners.items() if name not in in_bd])
    await session.commit()

async def orm_get_banners(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_add_image(session: AsyncSession, image: str, name: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()

async def orm_get_banner(session: AsyncSession, menu_name: str):
    query = select(Banner).where(Banner.name == menu_name)
    result = await session.execute(query)
    return result.scalar()

##################################### Создание атрибутов ######################################################

def get_sym_bg():
    headers = {"User-Agent":
                   "mozilla/5.0 (Windows; U; Windows NT 6.1; en-Us; rv:1.9.1.5"}
    url = "https://fragment.com/gifts/astralshard"
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    data = soup.find("main", class_="tm-main tm-main-catalog")

    syms = data.find_all("div", class_="tm-main-filters-item js-attribute-item")

    res_syms = []
    res_bgs = []

    for sym in syms:
        t = str(sym.find("div", class_="tm-main-filters-photo"))
        if "symbol" in t:
            res_syms.append(sym.get("data-value"))
        elif "backdrop" in t:
            res_bgs.append(sym.get("data-value"))
    return res_syms, res_bgs


async def orm_create_bg(session: AsyncSession):
    query = select(Bg)
    res = await session.execute(query)
    syms, bgs = get_sym_bg()

    if res.first():
        return

    for bg in bgs:
        session.add(Bg(name=bg))
    await session.commit()

async def orm_create_sym(session: AsyncSession):
    query = select(Symbol)
    syms, bgs = get_sym_bg()
    res = await session.execute(query)

    if res.first():
        return

    for sym in syms:

        session.add(Symbol(name=sym))
    await session.commit()

# Получение узора или фона

async def orm_get_all_symbols(session: AsyncSession):
    query = select(Symbol)
    res = await session.execute(query)
    return res.scalars().all()


async def orm_get_all_bgs(session: AsyncSession):
    query = select(Bg)
    res = await session.execute(query)
    return res.scalars().all()



############################# Получение нфт ############################################################

def is_ok_data(query, data, atribute, base):
    if data.get(atribute) != None:

        if len(data[atribute]) == 1:
            return query.where(base == data[atribute][0])
        else:
            return query.filter(base.in_(data[atribute]))
    return query


async def fetch_gift_data(
        session: ClientSession, url: str,
        semaphore: asyncio.Semaphore, session_db: AsyncSession,
        name_gift: str, num_gift: int) -> dict:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
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
        await asyncio.sleep(10)
        await fetch_gift_data(session, url, semaphore, session_db, name_gift, num_gift)


async def orm_create_nft(name_gift: str, session_db: AsyncSession):
    
    query = select(Gift).where(Gift.name == name_gift)
    result = await session_db.execute(query)

    all_gifts_in_db = result.scalars().all()
    
    added_gifts = [gift.num for gift in all_gifts_in_db]


    semaphore = asyncio.Semaphore(20)
    max_gift_num = max_num_gift(name_gift)
    name_gift = name_gift.replace(' ', '').replace('-', '')

    async with ClientSession() as session:
        tasks = []

        for num_gift in range(max_gift_num, 0, -1):
            if num_gift in added_gifts:
                continue


            task = asyncio.create_task(
                fetch_gift_data(session,
                                f"https://t.me/nft/{name_gift}-{num_gift}",
                                semaphore,
                                session_db, name_gift, num_gift))
            
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        await session_db.commit()


async def orm_search_nft(session: AsyncSession, name_nft: str, last_num:int, data: dict):
    print(last_num, data)
    query = select(Gift).where(Gift.name == name_nft)

    if data is not None:
        query = is_ok_data(query, data, "Model",Gift.model)
        query = is_ok_data(query, data, "Symbol",Gift.symbol)
        query = is_ok_data(query, data, "Bg", Gift.bg)

    #Для максимального количества пагинаций
    for_max_len = await session.execute(query)
    max_len = len(for_max_len.scalars().all())

    #Одна из страниц пагинации.
    result = await session.execute(query.offset(last_num).limit(15))
    l = result.scalars().all()
    list_nfts = []
    for nft in l:
        
        list_nfts.append(TextLink(nft.name + "  " + "#" + str(nft.num),
                                     url=f"https://t.me/nft/{nft.name.replace(" ", "").replace("-", "")}-{nft.num}")+
                         f"\nМодель: {nft.model}\n"
                         f"Узор: {nft.symbol}\n"
                         f"Фон: {nft.bg}\n")

    return list_nfts, max_len


################## Создание/изменение админа ########################################
async def orm_create_admin(session: AsyncSession, user_id: int):
    query = select(Admins).where(Admins.admin_id == user_id)
    result = await session.execute(query)

    if result.first():
        return

    session.add(Admins(admin_id=user_id))
    await session.commit()

async def orm_get_owner(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)

    owner = result.scalars().all()[0]
    return owner

async def orm_get_admins(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)
    admins_list = result.scalars().all()

    return [admin.admin_id for admin in admins_list]


async def orm_get_list_admins(session: AsyncSession, last_num: int = 0):
    query = select(Admins)
    result = await session.execute(query.offset(last_num).limit(20))
    admins = result.scalars().all()

    adm_list = [TextLink(admin.admin_id, url=f"tg://user?id={admin.admin_id}") for admin in admins]
    admins_list = as_list(as_marked_section("Админы: ",*adm_list, marker="- "))
    return admins_list



############################## Добавление всех названий подарков ########################################

async def orm_create_name_gift(session: AsyncSession):

    gifts = find_all_gifts()
    
    query = select(NameGift)
    result = await session.execute(query)
    gifts_db = result.scalars().all()
    print(len(gifts_db),len(gifts))
    if len(gifts_db) == len(gifts):
        return

    for gift in gifts:
        if gift in gifts_db:
            continue
        session.add(NameGift(name=gift))

    await session.commit()

async def orm_get_all_names_gift(session: AsyncSession):
    query = select(NameGift)
    result = await session.execute(query)

    return result.scalars().all()