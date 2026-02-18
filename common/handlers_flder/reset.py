from aiogram import F, Router

from aiogram.types import Message

from db.engine import engine as eng
from db.models import Base


handler_router = Router()



@handler_router.message(F.text == '/reset')
async def reset(message: Message):
    await message.answer('удаление')
    async def reset_db():
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    await reset_db()








