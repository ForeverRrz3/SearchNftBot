import os

from common.text_for_db import banner, admin
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker

from database.models import Gift, Banner, Bg, Symbol, Admins
from database.orm_query import orm_create_banners, orm_create_sym, orm_create_bg, orm_create_admin

engine = create_async_engine(os.getenv("DB_URL"),echo=True)

session_maker = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def create_db():
    async with (engine.begin() as conn):
        await conn.run_sync(Gift.metadata.create_all)
        await conn.run_sync(Banner.metadata.create_all)
        await conn.run_sync(Symbol.metadata.create_all)
        await conn.run_sync(Bg.metadata.create_all)
        await conn.run_sync(Admins.metadata.create_all)

    async with session_maker() as session:
        await orm_create_admin(session, admin[0])
        await orm_create_banners(session, banner)
        await orm_create_sym(session)
        await orm_create_bg(session)



async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Gift.metadata.drop_all)
        await conn.run_sync(Bg.metadata.drop_all)
        await conn.run_sync(Symbol.metadata.drop_all)