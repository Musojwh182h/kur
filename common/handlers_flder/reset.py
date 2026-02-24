from aiogram import F, Router

from aiogram.types import Message, CallbackQuery

from db.engine import engine as eng
from db.models import Base


handler_router = Router()



@handler_router.callback_query(F.data == 'reset')
async def reset(callback:CallbackQuery):
    await callback.message.answer('удаление')
    async def reset_db():
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    await reset_db()








