from datetime import datetime


from aiogram.utils.formatting import TextLink, as_marked_list, as_list, as_marked_section
from sqlalchemy.ext.asyncio import AsyncSession
from requests import *
from bs4 import BeautifulSoup
from random import randint

from time import sleep
from aiogram import types
from database.models import Gift, Banner, Symbol, Bg, Admins
from sqlalchemy import select,update,delete, values

from aiogram import Bot
from list_gift.find_gifts import max_num_gift
from list_gift.info_gifts import find_gift_info



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
    l = result.scalars().all()
    if result.first() and len(l) == len(banners.values()):
        return

    in_bd = [banner.name for banner in l]
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
    print(len(l))
    list_nfts = []
    for nft in l:
        print(nft.num, nft)
        list_nfts.append(TextLink(nft.name + "  " + "#" + str(nft.num),
                                     url=f"https://t.me/nft/{nft.name.replace(" ", "").replace("-", "")}-{nft.num}")+
                         f"\nМодель: {nft.model}\n"
                         f"Узор: {nft.symbol}\n"
                         f"Фон: {nft.bg}\n")

    return list_nfts, max_len

async def orm_create_nft(session: AsyncSession, name_nft: str, callback: types.CallbackQuery, bot: Bot):
    user = callback.from_user.id
    query = select(Gift).where(Gift.name == name_nft)
    res = await session.execute(query)
    l = res.scalars().all()
    print(len(l))
    problems = []
    max_num = max_num_gift(name_nft)

    if res.first() and len(l) == max_num:
        return False
    m = [nft.num for nft in l]
    cnt = 0
    for i in range(len(l)+1, max_num + 1):
        if i in m:
            continue

        cnt +=1
        try:
            res = find_gift_info(name_nft, i)
            print(max_num, i)
            session.add(Gift(name
                                  =name_nft, num=i, model=res["Model"],symbol=res["Symbol"],bg=res["Bg"]))

            if cnt%1000==0:
                sleep(randint(3,20))
                await bot.send_message(text=f"Уже сохранено: {i} {name_nft}, {str(datetime.now())[11:-7]}",chat_id=user)
            if cnt % 8000 == 0:
                await session.commit()
        except IndexError as e:
            await bot.send_message(text=f"Нет подарка под номером: t.me/nft/{name_nft}-{i}", chat_id=user)
        except Exception as e:
            problems.append(i)
            await bot.send_message(text=f"Возникла ошибка: {e}. Подарок под номером: {i}", chat_id=user)

    while problems:
        for i in problems[:]:
            try:
                res = find_gift_info(name_nft, i)
                print(max_num, i)
                session.add(Gift(name
                                      =name_nft, num=i, model=res["Model"],symbol=res["Symbol"],bg=res["Bg"]))

                if i%1000==0:
                    sleep(randint(1,7))
                    await bot.send_message(text=f"Уже сохранено: {i} {name_nft}, {str(datetime.now())[11:-7]}",chat_id=user)

                problems.remove(i)
            except Exception as e:
                problems.append(i)
                await bot.send_message(text=f"Возникла ошибка: {e}. Подарок под номером: {i}",chat_id=user)

    await session.commit()
    return True

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
    print(adm_list,"FUGSDIUFYDFGUYDGFUFKJGDSYHFDUFHGDUYFGDUYFGDYUFGDFUYGDYUFGSDYUFGSDUYFGSDUFYGDIF")
    return admins_list

