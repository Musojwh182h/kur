from db.models import User, Referal
from sqlalchemy import select
import logging
logger = logging.getLogger(__name__)


class RerferalService:
    def __init__(self, session, client):
        self.session = session
        self.client = client

    async def create_referal(self, tg, invited):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg))
            ref = await self.session.scalar(select(Referal).where(Referal.ref_tg_id == tg))
            if ref:
                logger.warning(f"Пользователь {tg} уже имеет реферала. Создание нового реферала не разрешено.")
                return
        
            ref = Referal(ref_tg_id=tg, invited_by_tg_id=invited, bonus_given=False, user_id=user.id)
            self.session.add(ref)
            await self.session.commit()
        except Exception as e:
            logging.exception(e)
            return None
    async def get_referal(self, tg):
        try:    
            return await self.session.scalar(select(Referal).where(Referal.ref_tg_id == tg))
        except Exception as e:
            logging.exception(e)
            return None
    
    
    