from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from ServiceClasses.subscription_service import SubscrService
from ServiceClasses.user_service import UserService
from ServiceClasses.vpn_service import VPNService
from ServiceClasses.shoping_service import ShopingService
from dotenv import load_dotenv
import os
load_dotenv() 
from db.engine import AsyncSessionMaker
puy_router = Router()

import logging
logger = logging.getLogger(__name__)
from py3xui import AsyncApi


class Buy(StatesGroup):
    buy = State()

@puy_router.callback_query(F.data == 'puy', Buy.buy)
async def puy_vpn(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    time_butt= data['price']
    price = {1:30, 3:90, 6:180, 12:365}
    days = price[time_butt]
    await callback.message.edit_text('Спасибо за покупку!')
    time_shop = datetime.now()
    new_date = time_shop
    async with AsyncSessionMaker() as session:
        vpn = VPNService(session)
        sub = SubscrService(session)
        check_sub = await sub.get_sub(callback.from_user.id)
        if not check_sub:
             await callback.message.answer('Нажмите на команду /start')
             logger.warning(f"Попытка продлить подписку для несуществующего пользователя: {callback.from_user.id}")
             return
        await vpn.buy_vpn(callback.from_user.id, days)
        logger.info(f'Подписка продлена на {days} дней для пользователя: {callback.from_user.id}')
        user = UserService(session)
        shoping = ShopingService(session)
        user_id = await user.check_user(callback.from_user.id)
        price_shop = {1:149, 3:350, 6:600, 12:999}
        await shoping.create_shoping(price_shop[time_butt], new_date, user_id)
        logger.info(f'Запись о покупке добавлена для пользователя: {callback.from_user.id} с суммой: {price_shop[time_butt]} Р. и датой: {new_date}')
        await state.clear()