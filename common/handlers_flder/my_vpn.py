from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.engine import AsyncSessionMaker
from ServiceClasses.subscription_service import SubscrService
from ServiceClasses.vpn_service import VPNService
from py3xui import AsyncApi
from dotenv import load_dotenv
import os
load_dotenv() 
import logging
logger = logging.getLogger(__name__)
from aiogram.enums import ParseMode


my_vpn_router = Router()

@my_vpn_router.callback_query(F.data == 'my_prof_vpn')
async def my_vpn(callback: CallbackQuery):
    now = datetime.now()
    tg_user = callback.from_user.id
    tg_name = callback.from_user
    kb = InlineKeyboardBuilder()
    kb.button(text='Продлить', callback_data='back')
    keyb = InlineKeyboardBuilder()
    # keyb.button(text='📷QR-код', callback_data='qr_code')
    keyb.button(text='⬅Назад', callback_data='main_menu')
    keyb.adjust(1)
    
    async with AsyncSessionMaker() as session:
        sub = SubscrService(session)
        vpn = VPNService(session)
        sub = await sub.get_sub(tg_user)
        vpn = await vpn.get_vpn_account(tg_user)
        if not sub:
            await callback.message.answer('У вас нет активной подписки. Пожалуйста, приобретите её или нажмите /start, чтобы увидеть детали.')
            logger.info(f'Пользователь {tg_user} попытался просмотреть профиль без активной подписки.')
            return
        if vpn.expired_at < now:
            await callback.message.answer(f'⏳ Ваша подписка истекла! Продлите чтобы продолжить',reply_markup=kb.as_markup())
            sub.status = 'expired'
            await session.commit()
            logger.info(f'Подписка истекла для пользователя: {tg_user}')
            return
        await callback.message.answer(f'⏳ Действует до: {vpn.expired_at}\n🔑 Ключ доступа:\n<pre>{vpn.key}</pre>\n❗️Просто нажмите на ключ один раз, чтобы скопировать его и начать пользоваться',
                                parse_mode=ParseMode.HTML, reply_markup=keyb.as_markup())