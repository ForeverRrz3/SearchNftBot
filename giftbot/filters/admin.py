from aiogram.types import Message
from aiogram import Bot
from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Admins, Banner
from database.engine import session_maker

async def orm_get_admins(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)
    admins_list = result.scalars().all()

    return [admin.admin_id for admin in admins_list]


class IsAdmin(Filter):
    def __init__(self)  -> None:
        pass

    async def __call__(self, message: Message, bot: Bot, session: AsyncSession) -> bool:
        async with session_maker() as session:
            my_admins_list = await orm_get_admins(session)
            return message.from_user.id in my_admins_list
