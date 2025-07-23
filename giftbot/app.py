import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties

from dotenv import find_dotenv,load_dotenv
from aiogram.enums import ParseMode


from Middlewares.db import DataBaseSession


load_dotenv(find_dotenv())
from routers.private import private_router
from routers.admin import admin_router


from database.engine import create_db, session_maker

bot = Bot(os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(private_router)



async def on_startup(bot):

    # run_param = False
    # if run_param:
    #     await drop_db()

    await create_db()

async def on_shutdown(bot):
    print("Бот лег")

async def main():


    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker,bot=bot))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())




if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Exit")

