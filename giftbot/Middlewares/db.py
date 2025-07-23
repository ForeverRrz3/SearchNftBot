from typing import Callable,Awaitable,Dict,Any
from aiogram import BaseMiddleware
from aiogram.types import Message,TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram import Bot


class DataBaseSession(BaseMiddleware):
    def __init__(self,session_pool: async_sessionmaker, bot: Bot):
        self.session_pool = session_pool
        self.bot = bot

    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str,Any]],Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str,Any]
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            data["bot"] = self.bot
            return await handler(event,data)



