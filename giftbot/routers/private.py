
from aiogram.enums import ParseMode
from aiogram.utils.formatting import TextLink


from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup


from sqlalchemy.ext.asyncio import AsyncSession

from kbrd.inline_kb import (MenuCallback, \
    btns_add_admin, btns_accept_admin)
from routers.menu_processing import get_menu_content

from database.orm_query import (orm_get_banner, orm_get_owner, orm_create_admin, \
    orm_get_admins)



private_router = Router()


class Info_gift(StatesGroup):
    Model = State()
    Symbol = State()
    Bg = State()


#################################### Добавление в админку ################################################
@private_router.message(Command("try_admin"))
async def try_to_get_admin(message: types.Message, session: AsyncSession):
    admins = await orm_get_admins(session)
    if message.from_user.id in admins:
        await message.answer(text="Вы уже являетесь админом.")
        return
    kb = btns_add_admin()
    await message.answer(text="Вы уверены, что хотите стать админом? Заявка будет отправлена владельцу.", reply_markup=kb)


@private_router.callback_query(F.data.startswith("YesAdmin"))
async def yes_admin(callback: types.CallbackQuery, session: AsyncSession, bot: Bot):
    owner = await orm_get_owner(session)

    user = f"@{callback.from_user.username}, {callback.from_user.first_name} {callback.from_user.last_name}"

    kb = btns_accept_admin(user=callback.from_user.id)
    text = TextLink("Пользователь",url= f"tg://user?id={callback.from_user.id}")+ f":{user} хочет добавиться в админы. Добавить?"
    await bot.send_message(chat_id=owner.admin_id, text=text.as_html(), reply_markup=kb,parse_mode=ParseMode.HTML)



@private_router.callback_query(F.data.startswith("NoAdmin"))
async def no_admin(callback: types.CallbackQuery):
    await callback.message.answer(text="Заявление отозвано")



@private_router.callback_query(F.data.startswith("Accept"))
async def yes_admin(callback: types.CallbackQuery, session: AsyncSession, bot: Bot):
    text, user_id = callback.data.split("_")

    await orm_create_admin(session, int(user_id))

    await bot.send_message(chat_id=int(user_id),text="Поздравляем вы стали админом. Чтобы запустить команды админа, напишите /admin.")
    await callback.message.edit_text(text="Админ добавлен")



@private_router.callback_query(F.data.startswith("NoAccept"))
async def yes_admin(callback: types.CallbackQuery, bot: Bot):
    text, user_id = callback.data.split("_")

    await callback.message.answer(text="Заявление на встпуление в админы отклонено.")
    await bot.send_message(chat_id=int(user_id), text="Заявление на встпуление в админы отклонено.")


@private_router.message(CommandStart())
async def start(message :types.Message, session: AsyncSession,state: FSMContext):
    await state.clear()

    image, reply_markup = await get_menu_content(level=0, session=session, menu_name="main")

    await message.answer_photo(photo=image.media, caption=image.caption, reply_markup=reply_markup)
########################################################################################

async def menu_main(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession):
    image, reply_markup = await get_menu_content(level=callback_data.level,
                                                 menu_name=callback_data.menu_name,
                                                 session=session,
                                                 page=callback_data.page)

    await callback.message.edit_media(media=image, reply_markup=reply_markup)


async def message_for_user(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession):
    text, reply_markup = await get_menu_content(level=callback_data.level,
                                                menu_name=callback_data.menu_name,
                                                session=session,
                                                name_nft=callback_data.name_nft,
                                                last_num=callback_data.last_num,
                                                page=callback_data.page)
    await callback.message.edit_text(text=text,reply_markup=reply_markup)


async def from_media_to_text(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession):

    text, reply_markup = await get_menu_content(level=callback_data.level,
                                                menu_name=callback_data.menu_name,
                                                session=session,
                                                name_nft=callback_data.name_nft)

    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=reply_markup)


@private_router.callback_query(StateFilter(Info_gift.Model),MenuCallback.filter())
async def fsm_menu_model(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession, state: FSMContext):

    if callback_data.level < 3 and callback_data.menu_name not in ["remember", "search"]:
        await state.clear()
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "remember":

        await state.set_state(None)
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "search":

        data = await state.get_data()

        text, reply_markup = await get_menu_content(level=callback_data.level,
                                                    menu_name=callback_data.menu_name,
                                                    name_nft=callback_data.name_nft,
                                                    session=session,
                                                    last_num=callback_data.last_num,
                                                    data=data)
        await callback.message.edit_text(text=text, reply_markup=reply_markup,disable_web_page_preview=True)
    else:

        data = await state.get_data()

        atrib = data.setdefault('Model',[]) + [callback_data.name_atr]
        await state.update_data(Model=atrib)
        text, kb = await get_menu_content(level=callback_data.level,
                                          menu_name="model",
                                          session=session,
                                          name_nft=callback_data.name_nft,
                                          atributes=atrib,
                                          page=callback_data.page)


        await callback.message.edit_text(text=text, reply_markup=kb)



@private_router.callback_query(StateFilter(Info_gift.Symbol),MenuCallback.filter())
async def fsm_menu_symbol(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession, state: FSMContext):
    if callback_data.level < 3 and callback_data.menu_name not in ["remember", "search"]:
        await state.clear()
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "remember":
        #Если пользователь захотел сохранить один из атрибутов для поиска
        await state.set_state(None)
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "search":
        #Если пользователь выбрал поиск подарка

        data = await state.get_data()

        text, reply_markup = await get_menu_content(level=callback_data.level,
                                                    menu_name=callback_data.menu_name,
                                                    name_nft=callback_data.name_nft,
                                                    session=session,
                                                    last_num=callback_data.last_num,
                                                    data=data)
        await callback.message.edit_text(text=text, reply_markup=reply_markup,disable_web_page_preview=True)
    else:

        data = await state.get_data()
        atrib = data.setdefault('Symbol',[]) + [callback_data.name_atr]

        await state.update_data(Symbol=atrib)
        text, kb = await get_menu_content(level=callback_data.level,
                                          menu_name="symbol",
                                          session=session,
                                          name_nft=callback_data.name_nft,
                                          atributes=atrib,
                                          page=callback_data.page)



        await callback.message.edit_text(text=text, reply_markup=kb)



@private_router.callback_query(StateFilter(Info_gift.Bg),MenuCallback.filter())
async def fsm_menu_bg(callback: types.CallbackQuery, callback_data: MenuCallback, session: AsyncSession, state: FSMContext):
    if callback_data.level < 3 and callback_data.menu_name not in ["remember", "search"]:
        await state.clear()
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "remember":
        await state.set_state(None)
        await user_menu(callback, callback_data, session, state)
    elif callback_data.menu_name == "search":
        data = await state.get_data()

        text, reply_markup = await get_menu_content(
                               level=callback_data.level,
                               menu_name=callback_data.menu_name,
                                name_nft=callback_data.name_nft,
                                session=session,
                                last_num=callback_data.last_num,
                               data=data)


        await callback.message.edit_text(text=text, reply_markup=reply_markup,disable_web_page_preview=True)

    else:

        print(callback_data)
        data = await state.get_data()

        atrib = data.setdefault('Bg',[]) + [callback_data.name_atr]


        await state.update_data(Bg=atrib)

        text, kb = await get_menu_content(level=callback_data.level,
                                          menu_name="bg",
                                          session=session,
                                          name_nft=callback_data.name_nft,
                                          atributes=atrib,
                                          page=callback_data.page)
        await callback.message.edit_text(text=text, reply_markup=kb)



async def set_state_for_menu_name(menu_name: str, state: FSMContext):
    if any(i in menu_name for i in ["bg","model","symbol"]):
        if "model" in menu_name:
            await state.set_state(Info_gift.Model)
        elif "symbol" in menu_name:
            await state.set_state(Info_gift.Symbol)
        else:
            await state.set_state(Info_gift.Bg)

@private_router.callback_query(MenuCallback.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallback, session: AsyncSession, state: FSMContext):


    if callback_data.level == 0:
        # Глваное меню с картинкой

        await menu_main(callback, callback_data, session)


    elif callback_data.menu_name == "search":
        #Поиск по всем выбранным атрибутам
        data_about_nft = await state.get_data()

        text, reply_markup = await get_menu_content(level=callback_data.level,
                               menu_name=callback_data.menu_name,
                                name_nft=callback_data.name_nft,
                                session=session,
                                last_num=callback_data.last_num,
                               data=data_about_nft)

        await callback.message.edit_text(text=text, reply_markup=reply_markup,disable_web_page_preview=True)
        await state.clear()

    elif callback_data.level != 1:

        await message_for_user(callback, callback_data, session)
        #Если menu_name = одному из атрибутов, то будет установлено в фсм, если нет, то ничего не произойдет
        await set_state_for_menu_name(callback_data.menu_name, state)


    else:
        ############### Чтобы перейти от медиа сообщения к текстовому ####################
        await from_media_to_text(callback, callback_data, session)


















