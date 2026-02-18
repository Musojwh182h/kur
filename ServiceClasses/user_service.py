from db.models import User
from datetime import datetime
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session):
        self.session = session
        
    async def check_user(self, tg_user):
        user = await self.session.scalar(select(User).where(User.telegram_id == tg_user))
        if user:
            logger.info(f"Пользователь с Telegram ID {tg_user} найден в базе.")
        return user
    
    async def create_user(self, tg_user):
        user = User(telegram_id=tg_user, reg_date=datetime.now(), referal_count=0)
        self.session.add(user)
        await self.session.commit()
        logger.info(f"Новый пользователь создан: Telegram ID {tg_user}")

    async def referal_count_(self, tg):
        user = await self.check_user(tg)
        if not user:
            logger.warning(f"Пользователь с Telegram ID {tg} не найден. Счётчик рефералов не обновлён.")
            return
        user.referal_count += 1
        await self.session.commit()
        logger.info(f"Счётчик рефералов для пользователя {tg} увеличен. Новое значение: {user.referal_count}")
        