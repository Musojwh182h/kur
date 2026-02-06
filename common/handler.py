from random import randint
from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from common.keyboards import inl, inline_times, buy_kb, intsr
from db.engine import AsyncSessionMaker
from aiogram.types import BufferedInputFile
import aiosqlite
import random
from io import BytesIO
from datetime import timedelta, datetime
from sqlalchemy import select
from db.models import User, Subscription
from py3x import add_client, change_client
import os
import time
import qrcode
from datetime import datetime
from aiogram import Bot
handler_router = Router()

class Buy(StatesGroup):
    buy = State()


@handler_router.message(CommandStart())
async def start_cmd(message: Message):
    tg_user = message.from_user.id
    username = message.from_user.username if message.from_user.username else 'Не указан'

    expired = int((time.time() + 3 * 86400) * 1000)



    await add_client(tg_user, expired)

    photo_path = r'C:\Users\SKM\Documents\Bandicam\photo_2025-12-02_20-31-10.jpg'
    text = f'''Привет! 👋 Добро пожаловать на KUR VPN! 🚀
Хотите защиту в интернете? 🛡️
Или скорость без ограничений? ⚡
У нас есть всё, чтобы вы были онлайн безопасно и быстро! 😎
'''

    await message.answer_photo(
        photo=types.FSInputFile(
            path=photo_path
        ),
        caption=text,
        reply_markup=inl
    )

@handler_router.callback_query(F.data == 'buyvpn')
async def traffic(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Отлично! Выберите тариф, чтобы продолжить: 📦', reply_markup=inline_times())

@handler_router.callback_query(F.data.startswith("time_"))
async def time_choice(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Оплатить', callback_data='puy')
    kb.button(text='Назад', callback_data='back')
    kb.adjust(1)
    time_butt = int(callback.data.split('_')[1])
    price = {1:149, 3:350, 6:600, 12:999}
    
    await state.update_data(price=int(time_butt))
    await state.set_state(Buy.buy)
    text = f'''💎 Подписка VPN на {time_butt} мес.
📱 5 устройств
💳 К оплате: {price[time_butt]}
‼️ Если не загружается страница, выключите VPN и попробуйте снова

✅ После оплаты просто вернитесь в Telegram — ваша подписка продлится автоматически'''
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    

@handler_router.callback_query(F.data == 'puy', Buy.buy)
async def puy_vpn(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_butt= data['price']
    price = {1:30, 3:90, 6:180, 12:365}
    days = price[time_butt]
    await callback.answer()
    await change_client(days, callback.from_user.id)
    await callback.message.edit_text('Спасибо за покупку!', reply_markup=buy_kb)
    await state.clear()




@handler_router.callback_query(F.data == 'my_prof_vpn')
async def my_vpn(callback: CallbackQuery):
    now = datetime.now()
    tg_user = callback.from_user.id
    tg_name = callback.from_user
    keyb = InlineKeyboardBuilder()
    keyb.button(text='📷QR-код', callback_data='qr_code')
    keyb.button(text='⬅Назад', callback_data='main_menu')
    keyb.adjust(1)
    async with AsyncSessionMaker() as session:
        stmt = select(Subscription).where(tg_user == Subscription.subs_tg_id)
        result = await session.execute(stmt)
        sub = result.scalar_one_or_none()
        if sub.expired < now:
            await callback.message.answer('Ваша подписка истекла!')
        await callback.message.answer(f'⏳ Действует до: {sub.expired}\n🔑 Ключ доступа:\n<pre>{sub.key}</pre>\n❗️Просто нажмите на ключ один раз, чтобы скопировать его и начать пользоваться',
                                parse_mode=ParseMode.HTML, reply_markup=keyb.as_markup())

 

@handler_router.callback_query(F.data == 'qr_code')
async def qr_code_image(callback: CallbackQuery, bot: Bot):
    kb = InlineKeyboardBuilder()
    kb.button(text='⬅Назад', callback_data='main_menu')
    async with AsyncSessionMaker() as session:
        sub = await session.scalar(select(Subscription).where(Subscription.subs_tg_id == callback.from_user.id))
        img = qrcode.make(sub.key)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        photo = BufferedInputFile(buffer.getvalue(), filename='qr.png')
        await callback.message.answer_photo(photo, caption='Отсканируйте QR-код, чтобы подключится', reply_markup=kb.as_markup())

    
        

@handler_router.callback_query(F.data =='instructions')
async def instr(callback: CallbackQuery):
    await callback.message.answer('Выерите устройство: ', reply_markup=intsr)







@handler_router.callback_query(F.data == 'back')
async def back_ck(callback: CallbackQuery):
    await callback.message.edit_text('Отлично! Выберите тариф, чтобы продолжить: 📦', reply_markup=inline_times())


@handler_router.callback_query(F.data == 'main_menu')
async def back(callback: CallbackQuery):
    photo_path = r'C:\Users\SKM\Documents\Bandicam\photo_2025-12-02_20-31-10.jpg'
    text = f'''Привет! 👋 Добро пожаловать на KUR VPN! 🚀
Хотите защиту в интернете? 🛡️
Или скорость без ограничений? ⚡
У нас есть всё, чтобы вы были онлайн безопасно и быстро! 😎
'''

    await callback.message.answer_photo(
        photo=types.FSInputFile(
            path=photo_path
        ),
        caption=text,
        reply_markup=inl)



