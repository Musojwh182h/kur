from random import randint
from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from common.keyboards import inl, inline_times, buy_kb, intsr, res
from db.engine import AsyncSessionMaker
from aiogram.types import BufferedInputFile
import aiosqlite
import random
from io import BytesIO
from datetime import timedelta, datetime
import asyncio
from sqlalchemy import select
from dotenv import load_dotenv
import os
load_dotenv() 
from db.models import User, Subscription, Shoping, Referal
# from py3x import add_client, change_client, referal
import os
import time
from ServiceClasses.subscription_service import SubscrService
from ServiceClasses.user_service import UserService
from ServiceClasses.vpn_service import VPNService
from ServiceClasses.shoping_service import ShopingService
from ServiceClasses.referal_service import RerferalService
import asyncio
from db.engine import engine as eng
from db.models import Base
import qrcode
from datetime import datetime, timezone
from aiogram import Bot
from py3xui import Api, AsyncApi, Inbound, Client
import logging
handler_router = Router()

class Buy(StatesGroup):
    buy = State()

logger = logging.getLogger(__name__)

api = AsyncApi(
    host=os.getenv('API_HOST'),
    username=os.getenv('API_USERNAME'),
    password=os.getenv('API_PASSWORD')
)



@handler_router.message(CommandStart())
async def start_cmd(message: Message, command: CommandObject):
    tg_user = message.from_user.id
    expired = int((time.time() + 3 * 86400) * 1000)
    async with AsyncSessionMaker() as session:
        user = UserService(session)
        client = VPNService(api)
        sub = SubscrService(session, client)
        ref = RerferalService(session, client)
        user_id = await user.check_user(tg_user)
        if not user_id:
            await user.create_user(tg_user)
            logger.info(f"Пользователь с Telegram ID {tg_user} создан в базе данных.")
            await client.startup()
            logger.info(f"Inbound {client.inbound} инициализирован для пользователя")
            client_key = await client.create_client(tg_user, expired)
            logger.info(f"Клиент создан для пользователя: {tg_user} с именем: {client_key.email}")                                                                                                                                                                                                                     
            key = await sub.create_key(client_key)                                                      
            await sub.create_sub(expired, tg_user,  key, client_key)
            logger.info(f"Подписка создана для пользователя: {tg_user} с ключом: {key}")
        if command.args:
            try:
                value = command.args.split()
                invited_id = int(value[0])
            except (ValueError, IndexError):
                await message.answer('Неправильная ссылка')
                logger.warning(f"Такая ссылка не правильная: {command.args} от пользователя: {tg_user}")
                return
            
            if tg_user != invited_id:
                check_user = await user.check_user(invited_id)                
                if not check_user:
                    logger.warning(f'Такой пригласивший пользователь не найден: {invited_id} для приглашающего пользователя: {tg_user}')
                    return None
                await ref.create_referal(tg_user, invited_id)
                logger.info(f'Создан реферал для пользователя: {tg_user} приглашённым пользователем: {invited_id}')
                ref_tg = await ref.get_referal(tg_user)
                sub_tg = await sub.get_sub(invited_id)
                if ref_tg and not ref_tg.bonus_given:
                    await sub.ref_client(sub_tg, api, ref_tg)
                    logger.info(f'Реферальный бонус применён для пользователя: {invited_id} за приглашённого пользователя: {tg_user}')
                    await user.referal_count_(ref_tg.invited_by_tg_id)      
                else:
                    return None      

    photo_path = r'C:\Users\SKM\Documents\Bandicam\photo_2025-12-02_20-31-10.jpg'
    text = f'''Привет! 👋 Добро пожаловать на KUR VPN! 🚀
Хотите защиту в интернете? 🛡️
Или скорость без ограничений? ⚡
У нас есть всё, чтобы вы были онлайн безопасно и быстро! 😎
'''

    mes = await message.answer_photo(
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
💳 К оплате: {price[time_butt]}Р.
‼️ Если не загружается страница, выключите VPN и попробуйте снова

✅ После оплаты просто вернитесь в Telegram — ваша подписка продлится автоматически'''
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    
@handler_router.callback_query(F.data == 'history_shop')
async def history_shoping(callback: CallbackQuery):
     async with AsyncSessionMaker() as session:
        user = UserService(session)
        shoping = ShopingService(session)
        user_id = await user.check_user(callback.from_user.id)
        shops = await shoping.get_shoping(user_id)
        if not shops:
               await callback.message.answer('У вас пока нету покупок')
               logger.info(f"Пользователь {callback.from_user.id} запросил историю покупок, но покупок не найдено.")
               return
        for shop in shops:
            text = f'''
Куплено в {shop.shop_date}.
Потрачено {shop.money} Р.'''
            await callback.message.answer(text)


@handler_router.callback_query(F.data == 'referal')
async def referal_system(callback:CallbackQuery):
     async with AsyncSessionMaker() as session:
        user = UserService(session)
        check_user = await user.check_user(callback.from_user.id)
        if not check_user:
            await callback.message.answer('Нажмите на команду /start')
            logger.warning(f"Попытка доступа к реферальной системе для несуществующего пользователя: {callback.from_user.id}")
            return
     await callback.message.answer(f'''🔥 Мы дарим VPN за друзей!
Каждый приглашённый: +5 дней подписки в подарок 💫

⚡️ Поделитесь ссылкой →

👥 Друг регистрируется →

🎁 Получайте дни бесплатно!

Приглашено пользователей: {check_user.referal_count}
                                    
Ваша реферельная ссылка:
<pre>https://t.me/@botintestin_bot?start={callback.from_user.id}</pre>
                                   
''', parse_mode=ParseMode.HTML)






@handler_router.callback_query(F.data == 'puy', Buy.buy)
async def puy_vpn(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_butt= data['price']
    price = {1:30, 3:90, 6:180, 12:365}
    days = price[time_butt]
    await callback.message.edit_text('Спасибо за покупку!')
    time_shop = datetime.now(timezone.utc)
    new_date = time_shop.strftime('%Y-%m-%d %H:%M')
    async with AsyncSessionMaker() as session:
        client = VPNService(api)
        sub = SubscrService(session, client)
        check_sub = await sub.get_sub(callback.from_user.id)
        if not check_sub:
             await callback.message.answer('Нажмите на команду /start')
             logger.warning(f"Попытка продлить подписку для несуществующего пользователя: {callback.from_user.id}")
             return
        await client.startup()
        await sub.change_client(days, callback.from_user.id, api)
        logger.info(f'Подписка продлена на {days} дней для пользователя: {callback.from_user.id}')
        user = UserService(session)
        shoping = ShopingService(session)
        user_id = await user.check_user(callback.from_user.id)
        price_shop = {1:149, 3:350, 6:600, 12:999}
        await shoping.create_shoping(price_shop[time_butt], new_date, user_id)
        logger.info(f'Запись о покупке добавлена для пользователя: {callback.from_user.id} с суммой: {price_shop[time_butt]} Р. и датой: {new_date}')
        await state.clear()




@handler_router.callback_query(F.data == 'my_prof_vpn')
async def my_vpn(callback: CallbackQuery, bot: Bot):
    now = datetime.now()
    tg_user = callback.from_user.id
    tg_name = callback.from_user
    kb = InlineKeyboardBuilder()
    kb.button(text='Продлить', callback_data='back')
    keyb = InlineKeyboardBuilder()
    keyb.button(text='📷QR-код', callback_data='qr_code')
    keyb.button(text='⬅Назад', callback_data='main_menu')
    keyb.adjust(1)
    
    async with AsyncSessionMaker() as session:
        stmt = select(Subscription).where(Subscription.subs_tg_id == tg_user)
        result = await session.execute(stmt)
        sub = result.scalar_one_or_none()
        if not sub:
            await callback.message.answer('У вас нет активной подписки. Пожалуйста, приобретите её или нажмите /start, чтобы увидеть детали.')
            logger.info(f'Пользователь {tg_user} попытался просмотреть профиль без активной подписки.')
            return
        if sub.expired < now:
            await callback.message.answer(f'⏳ Ваша подписка истекла! Продлите чтобы продолжить',reply_markup=kb.as_markup())
            logger.info(f'Подписка истекла для пользователя: {tg_user}')
            return
        await callback.message.answer(f'⏳ Действует до: {sub.expired}\n🔑 Ключ доступа:\n<pre>{sub.key}</pre>\n❗️Просто нажмите на ключ один раз, чтобы скопировать его и начать пользоваться',
                                parse_mode=ParseMode.HTML, reply_markup=keyb.as_markup())


@handler_router.callback_query(F.data == 'qr_code')
async def qr_code_image(callback: CallbackQuery, bot: Bot):
    try:
        async with AsyncSessionMaker() as session:
            sub  = SubscrService(session, VPNService(api))
            sub = await sub.get_sub(callback.from_user.id)
            if not sub:
                await callback.message.answer('У вас нет активной подписки. Пожалуйста, приобретите её или нажмите /start чтобы увидеть детали.')
                logger.info(f'Пользователь {callback.from_user.id} попытался просмотреть QR-код без активной подписки.')
                return
            img = qrcode.make(sub.key)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            photo = BufferedInputFile(buffer.getvalue(), filename='qr.png')
            await callback.message.answer_photo(photo, caption='Отсканируйте QR-код, чтобы подключится')
    except Exception:
                 await callback.message.answer('Чтобы продолжить, нажмите /start')
                 return
    
        

@handler_router.callback_query(F.data =='instructions')
async def instr(callback: CallbackQuery):
    await callback.message.edit_text('Выерите устройство: ', reply_markup=intsr)



@handler_router.message(F.text == '/reset')
async def reset(message: Message):
    await message.answer('удаление')
    async def reset_db():
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    await reset_db()



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



