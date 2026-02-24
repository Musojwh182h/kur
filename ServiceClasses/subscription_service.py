from db.models import User, Subscription
from sqlalchemy import select
from datetime import datetime
import time
import logging
logger = logging.getLogger(__name__)
class SubscrService:
    def __init__(self, session):
        self.session = session

    async def create_sub(self, tg_id):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg_id))
            if not user:
                return None
            sub = Subscription(created_at=datetime.now(), status='active', user_id=user.id)
            self.session.add(sub)
            await self.session.commit()
        except Exception as e:
            logging.exception(e)
            return None

    async def get_sub(self, tg):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg))
            if not user:
                return None
            return await self.session.scalar(select(Subscription).where(Subscription.user_id == user.id))
        except Exception as e:
            logging.exception(e)
            return None