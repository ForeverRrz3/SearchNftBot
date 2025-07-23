

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from common.payments import PAYMENT


from utility.paginator import Paginator


class StarsCallback(CallbackData,prefix="stars"):
    level: int
    username: str | None = None
    menu_name: str | None = None
    cnt: int | str | None = None
    payment: str | None = None


class AdminCallback(CallbackData, prefix="admin"):
    username: str | None = None
    user_id: int | None = None
    name_nft: str | None
    answer: str | None = None

class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    page: int = 1
    name_nft: str | None = None
    name_atr: str | None = None
    last_num: int = 0

def main_menu_kb(level: int):

    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="О нас",
                                callback_data=MenuCallback(level=0,menu_name="about").pack()))
    kb.add(InlineKeyboardButton(text="Поиск нфт",
                                callback_data=MenuCallback(level=level+1, menu_name="name_nft").pack()))
    kb.add(InlineKeyboardButton(text="Покупка звезд",
                                callback_data=StarsCallback(level=5, menu_name="buying_stars").pack()))
    return kb.adjust(2,1).as_markup()



def btns_name_nft(names: list, level:int, sizes = (3,)):

    kb = InlineKeyboardBuilder()

    for name in names:
        kb.add(InlineKeyboardButton(text=name,
                                    callback_data=MenuCallback(level=level+1,menu_name="MenuNft",name_nft=name).pack()))

    kb.add(InlineKeyboardButton(text="Обратно ⬅️",
                                callback_data=MenuCallback(level=level-1, menu_name="about").pack()))

    return kb.adjust(*sizes).as_markup()


def get_atributes(atrib:dict, level: int, name_nft: str):
    # Выызгрузка выбранного атрибута

    kb = InlineKeyboardBuilder()

    for text,at in atrib.items():
        kb.add(InlineKeyboardButton(text=text,
                                    callback_data=MenuCallback(level=level+1, name_nft=name_nft, menu_name=at).pack()))

    kb.add(InlineKeyboardButton(text="Обратно ⬅️",
                                callback_data=MenuCallback(level=level - 1, menu_name="about").pack()))
    kb.add(InlineKeyboardButton(text="Поиск 🔎",
                                callback_data=MenuCallback(level=4, menu_name="search", name_nft=name_nft).pack()))

    return kb.adjust(2,2,1).as_markup()



def fsm_btns_atributes_nft(names: list, level: int, name_menu: str, name_nft: str, atributes: list, page: int, sizes = (3,)):

    kb = InlineKeyboardBuilder()

    paginator = Paginator(names, 60, page)
    btns = pages(paginator)


    if len(names) > 60 and page == 1:
        names = paginator.get_first()
    elif len(names) > 60:
        names = paginator.get_next()

    for model in names:
        if model in atributes:
            if len(model) > 12:
                model = model[:11]
            kb.add(InlineKeyboardButton(text="✅"+model,
                                        callback_data=MenuCallback(level=level, menu_name=name_menu, name_nft=name_nft,
                                                                   name_atr=model).pack()))
        else:

            kb.add(InlineKeyboardButton(text=model,
                                    callback_data=MenuCallback(level=level,menu_name=name_menu,name_nft=name_nft, name_atr=model).pack()))


    kb.adjust(*sizes)
    row1 = []

    row1.append(InlineKeyboardButton(text="Обратно ⬅️",
                                     callback_data=MenuCallback(level=2, menu_name="MenuNft",
                                                                name_nft=name_nft).pack()))
    row1.append(InlineKeyboardButton(text="На главную 🏠",
                                     callback_data=MenuCallback(level=0, menu_name="main").pack()))

    row1.append(InlineKeyboardButton(text="Поиск 🔎",
                                     callback_data=MenuCallback(level=4, menu_name="search", name_nft=name_nft).pack()))

    kb.row(*row1)

    row2 = []


    for name, text in btns.items():

        if name == "back":
            row2.append(InlineKeyboardButton(text=text,
                                             callback_data=MenuCallback(level=3, menu_name=name_menu,
                                                                        name_nft=name_nft, page=page - 1).pack()))
        if name == "next":
            row2.append(InlineKeyboardButton(text=text,
                                             callback_data=MenuCallback(level=3, menu_name=name_menu,
                                                                        name_nft=name_nft, page=page + 1).pack()))

    row2.append((InlineKeyboardButton(text="Сохранить 💾",
                                      callback_data=MenuCallback(level=2, menu_name="remember",
                                                                 name_nft=name_nft).pack())))
    return kb.row(*row2).as_markup()



def pages(paginator):

    btns = {}

    if paginator.has_previous():
        btns["back"] = "<--"

    if paginator.has_next():
        btns["next"] = "-->"

    return btns


def btns_search_nft(
        *,
        name_nft: str,
        last_num: int,
        max_len: int,
        sizes: tuple[int] = (2,)
):

    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="На главную 🏠",
                                callback_data=MenuCallback(level=0, menu_name="main").pack()))

    kb.adjust(*sizes)

    row = []
    if last_num > 15: #Если можно пойти назад, то добавляем кнопку назад
        row.append(InlineKeyboardButton(text="<--",
                                        callback_data=MenuCallback(level=4,name_nft=name_nft, menu_name="search",last_num=last_num-15).pack()))

    row.append(InlineKeyboardButton(text='Канал',url="https://t.me/PlataStarDep"))
    if last_num + 15 < max_len: #Если есть еще, то добавляем кнопку вперед
        row.append(InlineKeyboardButton(text="-->",
                                        callback_data=MenuCallback(level=4,name_nft=name_nft, menu_name="search",last_num=last_num+15).pack()))


    return kb.row(*row).as_markup()


def btns_buying_stars(
        *,
        level:int,
        menu_name: str,
        sizes: tuple[int] = (3,2)
):

    kb = InlineKeyboardBuilder()

    stars = ["50","100","250","500","1000","Другое"]
    for cnt in stars:
        if cnt == "Другое":
            kb.add(InlineKeyboardButton(text=cnt,
                                        callback_data=StarsCallback(count="another",level=level,menu_name=menu_name).pack()))
        else:
            kb.add(InlineKeyboardButton(text=cnt+"⭐",
                                callback_data=StarsCallback(cnt=int(cnt),level=level+1,menu_name=menu_name).pack()))
    kb.adjust(*sizes)

    return kb.row(InlineKeyboardButton(text="На главную 🏠",
                                callback_data=MenuCallback(level=0, menu_name="main").pack())).as_markup()



def btns_cnt_stars(*,
                   level: int,
                   cnt_stars: int,
                   user: str,
                   menu_name: str,
                   sizes: tuple[int] = (2,)):

    kb = InlineKeyboardBuilder()


    kb.add(InlineKeyboardButton(text=f"Количество: {cnt_stars}⭐",
           callback_data=StarsCallback(level=5, username=user, menu_name=menu_name).pack()))
    kb.add(InlineKeyboardButton(text=f"Кому: @{user}",
                                callback_data=StarsCallback(level=level, username="@"+user.replace("@",""), menu_name="username",cnt=cnt_stars).pack()))
    kb.add(InlineKeyboardButton(text="Купить",
                                callback_data=StarsCallback(level=level+1,username=user,cnt=cnt_stars).pack()))

    kb.adjust(*sizes)

    return kb.row(InlineKeyboardButton(text="На главную 🏠",
                                       callback_data=MenuCallback(level=0, menu_name="main").pack())).as_markup()



def btns_username(level, user, cnt_stars):
    user = "@" + user
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text=f"Свой: {user}",
                                callback_data=StarsCallback(level=level,cnt=cnt_stars, username=user, menu_name="buying_stars").pack()))
    kb.add(InlineKeyboardButton(text="На главную 🏠",
                                       callback_data=MenuCallback(level=0, menu_name="main").pack()))
    return kb.adjust(*(1,)).as_markup()


def btns_payment(level, menu_name, user, cnt_stars, sizes = (2,)):
    kb = InlineKeyboardBuilder()

    for pay in PAYMENT:
        kb.add(InlineKeyboardButton(text=pay,
                                    callback_data=StarsCallback(level=level,cnt=cnt_stars,menu_name=pay,username=user,payment=pay).pack()))
    kb.add(InlineKeyboardButton(text="На главную 🏠",
                                       callback_data=MenuCallback(level=0, menu_name="main").pack()))

    return kb.adjust(*sizes).as_markup()

def inlinekb(
        *,
        btns: dict,
        sizes: tuple[int] = (2,),):
    kb = InlineKeyboardBuilder()
    for text, data in btns.items():
        if data == "find_nft":
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallback(level=2, menu_name=data).pack()))
        elif data == "buying_stars":
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallback(level=1,menu_name=data).pack()))
        else:
            kb.add(InlineKeyboardButton(text=text, callback_data=MenuCallback(level=1, menu_name=data).pack()))

    return kb.adjust(*sizes).as_markup()


def inline_url(*,
               btns: dict,
               sizes: tuple = (2,)):

    kb = InlineKeyboardBuilder()

    for text, url in btns.items():
        kb.add(InlineKeyboardButton(text=text, url=url))

    return kb.adjust(*sizes).as_markup()


def btns_add_admin(sizes: tuple = (2,)):

    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Да",callback_data="YesAdmin"))
    kb.add(InlineKeyboardButton(text="Нет",callback_data="NoAdmin"))

    return kb.adjust(*sizes).as_markup()

def admin_add_nft(
        *,
        btns: list,
        sizes: tuple[int] = (2,)
):

    kb = InlineKeyboardBuilder()

    for name in btns:
        kb.add(InlineKeyboardButton(text=name,
                                    callback_data=AdminCallback(name_nft=name).pack()))

    return kb.adjust(*sizes).as_markup()

def btns_accept_admin(user: int, sizes: tuple = (2,)):

    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Добавить", callback_data=f"Accept_{user}"))
    kb.add(InlineKeyboardButton(text="Отклонить", callback_data=f"NoAccept_{user}"))

    return kb.adjust(*sizes).as_markup()

def admin_answer(name_nft):
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text="Да, уверен",
                                callback_data=AdminCallback(name_nft=name_nft, answer="True").pack()))
    kb.add(InlineKeyboardButton(text="Нет, не надо",
                                callback_data=AdminCallback(name_nft=name_nft, answer="False").pack()))


    return kb.adjust(*(2,1)).as_markup()




