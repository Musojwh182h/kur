from aiogram import Bot
from datetime import datetime, timedelta
from db.models import Subscription
from db.engine import AsyncSessionMaker
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)
async def notifications(bot: Bot):
    
    now = datetime.now()
    one_day = now + timedelta(days=1)
    start_days = one_day.replace(hour=0, minute=0, second=0, microsecond=0)
    three_days = now + timedelta(days=3)
    end_days = three_days.replace(hour=23, minute=59, second=59, microsecond=9999999)
    async with AsyncSessionMaker() as session:
        subs = await session.scalars(select(Subscription).where((Subscription.expired >= start_days) & (Subscription.expired <= end_days)))
        for sub in subs.all():
            try:    
                await bot.send_message(chat_id=sub.subs_tg_id, text='Ваша подписка истекает')
                logger.info('Подписка истекает')
            except Exception:
                logger.info('Бот может быть заблокирован')