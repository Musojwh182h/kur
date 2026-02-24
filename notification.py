from aiogram import Bot
from datetime import datetime, timedelta
from db.models import Vpn_Account
from db.engine import AsyncSessionMaker
from sqlalchemy import select
import logging
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
import asyncio
logger = logging.getLogger(__name__)
async def notifications(bot: Bot):
    try:
        now = datetime.now()
        one_day = now + timedelta(days=1)
        start_days = one_day.replace(hour=0, minute=0, second=0, microsecond=0)
        three_days = now + timedelta(days=3)
        end_days = three_days.replace(hour=23, minute=59, second=59, microsecond=9999999)
        async with AsyncSessionMaker() as session:
            subs = await session.scalars(select(Vpn_Account).where((Vpn_Account.expired >= start_days) & (Vpn_Account.expired <= end_days)))
            for sub in subs.all():
                try:    
                    await bot.send_message(chat_id=sub.vpn_tg_id, text='Ваша подписка истекает, чтобы продолжить пользоваться услугой, пожалуйста продлите подписку')
                except TelegramRetryAfter as e:
                    asyncio.sleep(e.retry_after)
                    try:
                        await bot.send_message(chat_id=sub.vpn_tg_id, text='Ваша подписка истекает, чтобы продолжить пользоваться услугой, пожалуйста продлите подписку')
                    except TelegramForbiddenError:
                        continue
                except TelegramForbiddenError:
                    logger.exception('Бот может быть заблокирован')
                    continue
    except Exception as e:
        logging.exception(e)