from aiogram import Router, types, F
main_router = Router()
from aiogram.types import CallbackQuery
from common.text_handlers import text
import logging
from dotenv import load_dotenv
from common.keyboards import inl
from aiogram.enums import ParseMode
import os
load_dotenv() 
logger = logging.getLogger(__name__)



try:
    ADMIN = [
        int(v.strip())
        for v in os.getenv('ADMIN', '').split(',')
        if v.strip().isdigit()
    ]
except ValueError:
    logging.exception('Значение не является числом')
    

@main_router.callback_query(F.data == 'main_menu')
async def back(callback: CallbackQuery):
    kb = inl()
    if callback.from_user.id in ADMIN:
        kb.button(text='🛠 Админ-панель', callback_data='admin')
        kb.button(text='Рестартнуть', callback_data='reset')
        kb.adjust(1)
    await callback.message.answer('Приветствую вас в VPN! 🚀',
        reply_markup=kb.as_markup())
