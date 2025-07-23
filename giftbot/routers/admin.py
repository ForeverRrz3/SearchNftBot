
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types, F


from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from aiogram import Bot
from kbrd.kb import admin_kb
from kbrd.inline_kb import admin_add_nft, AdminCallback, admin_answer, btns_add_admin
from database.orm_query import orm_get_banners, orm_add_image, orm_create_nft, orm_create_admin, orm_get_list_admins
from list_gift.default import find_all_gifts
from list_gift.info_gifts import max_num_gift
from filters.admin import IsAdmin

admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.message(F.text.lower() == "просмотреть админов")
async def view_list_admins(message: types.Message, session: AsyncSession):

    admins_list = await orm_get_list_admins(session)
    await message.answer(text=admins_list.as_html())


############################## Добавление/изменение баннеров ########################################

class Banners(StatesGroup):
    image = State()

@admin_router.message(Command("admin"))
async def start_admin(message: types.Message):
    await message.answer("Что хотите сделать?",reply_markup=admin_kb)

@admin_router.callback_query(F.data.startswith("Start"))
async def start_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Что хотите сделать?",reply_markup=admin_kb)


@admin_router.message(F.text.lower() == "создать новый нфт")
async def add_new_nft(message: types.Message):

    nfts = find_all_gifts()

    kb = admin_add_nft(btns=nfts)
    await message.answer(text="Выберите модель для добавления в БД: ", reply_markup=kb)

@admin_router.callback_query(AdminCallback.filter(),F.data.endswith("False"))
async def answer_no(callback: types.CallbackQuery, callback_data: AdminCallback, session: AsyncSession):
    await callback.message.edit_text(text="Ок, отменено")

@admin_router.callback_query(AdminCallback.filter(),F.data.endswith("True"))
async def answer_yes(callback: types.CallbackQuery, callback_data: AdminCallback, session: AsyncSession, bot: Bot):
    await callback.message.edit_text(f"Выполняется добавление {callback_data.name_nft}")
    if callback_data.answer:
        # 12:59:33
        if await orm_create_nft(session, callback_data.name_nft, callback, bot):
            await callback.message.answer(f"Добавлен новый нфт - {callback_data.name_nft}")
        else:
            await callback.message.answer(f"Такой нфт уже есть - {callback_data.name_nft}")



@admin_router.callback_query(AdminCallback.filter())
async def add_new_nft_orm(callback: types.CallbackQuery, callback_data: AdminCallback, session: AsyncSession):
    max_num = max_num_gift(callback_data.name_nft)

    await callback.message.edit_text(text=f"{callback_data.name_nft} - {max_num}. Займет примерно {ceil(max_num*0.0035)} минут, уверены?", reply_markup=admin_answer(callback_data.name_nft))




@admin_router.message(StateFilter(None),F.text.lower() == "добавление/изменение баннера")
async def add_image_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    names = [banner.name for banner in await orm_get_banners(session)]
    await message.answer(f"Отправьте фото и напишите к чему оно относится: \n{', '.join(names)}")
    await state.set_state(Banners.image)

@admin_router.message(Banners.image, F.photo)
async def set_image(message: types.Message, state: FSMContext, session: AsyncSession):
    image = message.photo[-1].file_id
    text = message.caption.strip()
    names = [banner.name for banner in await orm_get_banners(session)]

    if text not in names:
        await message.answer(f"Введите нормальное название из предложенных: \n{', '.join(names)}")
        return

    await orm_add_image(session, image, text)
    await message.answer("Баннер изменен/добавлен")
    await state.clear()

@admin_router.message(Banners.image)
async def set_image2(message: types.Message):
    await message.answer("Отправьте фото")



class Admin(StatesGroup):
    user_id  = State()


@admin_router.message(F.text.lower() == "добавить админа")
async def add_admin(message: types.Message, state: FSMContext):

    kb = btns_add_admin()

    await message.answer(text="Отправьте @username админа или его user_id.",reply_markup=kb)
    await state.set_state(Admin.user_id)

@admin_router.message(Admin.user_id)
async def add_admin_base(message: types.Message, state: FSMContext, session: AsyncSession):

    if message.text[0] == "@":
        user_id = ...
    elif isinstance(message.text, int):
        user_id = int(message.text)
    else:
        return

    await orm_create_admin(session, user_id)
    await session.commit()

    await state.clear()

    kb = btns_add_admin()
    await message.answer(text="Введите @username или user_id пользователя!", reply_markup=kb)