
from aiogram.types import InputMediaPhoto, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.utils.formatting import as_list, as_marked_section

from kbrd.inline_kb import (main_menu_kb, btns_name_nft, get_atributes, btns_search_nft,
                            fsm_btns_atributes_nft)

from database.orm_query import orm_get_banner, orm_get_all_symbols, orm_get_all_bgs, orm_search_nft
from list_gift.default import find_all_gifts
from list_gift.info_gifts import get_all_models

async def menu_user(
        session:AsyncSession,
        menu_name: str,
        level:int
):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(caption=banner.description, media=banner.image)

    kb = main_menu_kb(level)

    return image, kb


async def search_all_name(session, level, menu_name):
    # Поиск всех названий подарков, парсятся с фрагмента, в будущем можно было добавить в бд
    names = find_all_gifts()
    text = "Выберите подарок для поиска"
    kb = btns_name_nft(names, level)

    return text, kb

async def menu_nft(session, level,name_nft):
    # Выбор атрибутов нфт

    atributes = {"Модель": "model", "Узор":"symbol", "Фон":"bg"}
    text = "Выберите по каким признакам искать подарок"

    kb = get_atributes(atributes, level, name_nft)

    return text, kb

######################### Получение атрибутов подарка #################################

async def get_models(level, name_nft,atributes, page):
    models = get_all_models(name_nft)

    text = "Выберите модель для поиска: "
    kb = fsm_btns_atributes_nft(models, level, "ChoosingMod", name_nft, atributes, page)

    return text, kb


async def get_symbol(session, level, name_nft,atributes, page):
    symbols = [sym.name for sym in await orm_get_all_symbols(session)]

    text = "Выберите узор для поиска: "
    kb = fsm_btns_atributes_nft(symbols, level, "ChoosingSym", name_nft,atributes, page)

    return text, kb


async def get_bg(session, level, name_nft,atributes, page):
    bgs = [sym.name for sym in await orm_get_all_bgs(session)]

    text = "Выберите фон для поиска: "
    kb = fsm_btns_atributes_nft(bgs, level, "ChoosingBg", name_nft, atributes, page)

    return text, kb


##########################################################

###################### Поиск нфт по атрибутам #################################

async def search_nft(session, name_nft, data, last_num):

    # Поиск нфт по выбранным атрибутам. Последний номер нужен для того, чтобы БД знало с какого номера осуществлять поиск
    nfts, max_len = await orm_search_nft(session, name_nft, last_num, data)

    marked_list= as_list(as_marked_section("Вот поиск по подаркам:\n",*nfts,
                                 marker="- ")).as_html()

    kb = btns_search_nft(name_nft=name_nft, last_num=last_num,max_len=max_len)

    return marked_list, kb






async def search_all_atributes(session, level, menu_name, name_nft, atributes, page):
    #Поиск всех моделей по названию атрибута. Узор и зданий фон сохранены в БД, а модели парсятся с фрагмента
    if menu_name == "model":
        return await get_models(level, name_nft,atributes, page)
    elif menu_name == "symbol":
        return await get_symbol(session, level,atributes, name_nft, page)
    elif menu_name == "bg":
        return await get_bg(session, level, name_nft,atributes, page)


async def get_menu_content(
        level: int ,
        menu_name: str,
        session: AsyncSession,
        page: int = 1,
        user: str = "",
        atributes: list = [],
        callback: CallbackQuery | None = None,
        last_num: int = 1,
        cnt_stars: int = 0,
        name_nft: str| None = None,
        data: dict | None = None):

    if level == 0:
        return await menu_user(session, menu_name, level)
    elif level == 1:
        return await search_all_name(session, level, menu_name)
    elif level == 2:
        return await menu_nft(session, level, name_nft)
    elif level == 3:
        return await search_all_atributes(session,level, menu_name, name_nft,atributes,page)
    elif level == 4:
        return await search_nft(session, name_nft, data, last_num)
