from db.models import Shoping
from sqlalchemy import select
import logging
logger = logging.getLogger(__name__)

class ShopingService:
    def __init__(self, session):
        self.session = session

    async def create_shoping(self, money, shop_date, user):
        try:
            shop = Shoping(shop_date=shop_date, money=money, user_id=user.id)
            self.session.add(shop)
            await self.session.commit()
            logger.info(f"Покупка создана: пользователь {user.id}, сумма {money} Р., дата {shop_date}")
        except Exception as e:
            logger.error(f"Ошибка при создании записи о покупке: {e}")
            raise

    async def get_shoping(self, user):
        if not user:
            logger.warning(f"Попытка получить покупки для None пользователя.")
            return
        try:
            stmt = await self.session.scalars(select(Shoping).where(Shoping.user_id == user.id)) 
            shops = stmt.all()
            logger.info(f"Получено {len(shops)} покупок для пользователя {user.id}")
            return shops
        except Exception as e:
            logger.error(f"Ошибка при получении покупок для пользователя {user.id}: {e}")
            raise
    
   