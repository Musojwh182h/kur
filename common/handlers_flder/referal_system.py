from aiogram import Router, F
from aiogram.types import CallbackQuery
from db.engine import AsyncSessionMaker
from ServiceClasses.user_service import UserService
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from common.text_handlers import referal_text
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

referal_router = Router()

@referal_router.callback_query(F.data == 'referal')
async def referal_system(callback:CallbackQuery):
     kb = InlineKeyboardBuilder()
     kb.button(text='🏠Меню', callback_data='main_menu')
     kb.adjust(1)
     async with AsyncSessionMaker() as session:
        user = UserService(session)
        check_user = await user.check_user(callback.from_user.id)
        if not check_user:
            await callback.message.answer('Нажмите на команду /start')
            logger.warning(f"Попытка доступа к реферальной системе для несуществующего пользователя: {callback.from_user.id}")
            return
     await callback.message.answer(text=referal_text(check_user, callback), parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())


