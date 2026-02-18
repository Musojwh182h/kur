from db.models import User, Subscription
from sqlalchemy import select
from datetime import timedelta, timezone, datetime, UTC
import time
import logging
logger = logging.getLogger(__name__)
class SubscrService:
    def __init__(self, session):
        self.session = session

    async def create_sub(self, tg_id):
        
        user = await self.session.scalar(select(User).where(User.telegram_id == tg_id))
        sub = Subscription(subs_tg_id=tg_id, created_at=datetime.now(UTC), status='active', user_id=user.id)
        self.session.add(sub)
        await self.session.commit()

    async def get_sub(self, tg):
        return await self.session.scalar(select(Subscription).where(Subscription.subs_tg_id == tg))
    
    # async def change_client(self, price, tg, api):
    # # try:
    #         sub = await self.get_sub(tg)
            
    #         if not self.client or not self.client.inbound:
    #             logger.warning(f"Клиент для пользователя {tg} не найден или не инициализирован. Попытка инициализации клиента.")
    #             await self.client.startup()
    #         now = datetime.now()
    #         try:
    #             client = None
    #             for i in self.client.inbound.settings.clients:
    #                 if i.id == sub.uuid:
    #                     client = i
    #                     break
    #         except Exception as e:
    #             logger.error(f"Ошибка при поиске клиента для пользователя {tg}: {e}")
    #             return
                
            
            
    #         if not sub:
    #             logger.warning(f"Подписка для пользователя {tg} не найдена. Невозможно изменить клиента.")
    #             return
            
    #         if sub.expired < now and client:
                
    #             sub.expired = now + timedelta(days=price)
    #             client.expiry_time = int((time.time() + price * 86400) * 1000)
                
    #         if sub.expired >= now and client:
    #             expiredd = price * 86400 * 1000
                
    #             sub.expired += timedelta(days=price)
    #             client.expiry_time += expiredd
    #         await api.inbound.update(self.client.inbound.id, self.client.inbound)
    #         await self.session.commit()

    # async def ref_client(self, res, api, ref):
    #         if not self.client or not self.client.inbound:
    #             await self.client.startup()
    #         try:
    #             client = None
    #             for i in self.client.inbound.settings.clients:
    #                 if i.id == res.uuid:
    #                     client = i
    #                     break
    #         except Exception as e:
    #             logger.error(f"Ошибка при поиске клиента для реферала {res.ref_tg_id}: {e}")   
    #         if not client:
    #             logger.warning(f"Клиент для реферала {res.ref_tg_id} не найден. Невозможно применить бонус.")
    #             return
    #         if ref.bonus_given == True:
    #             logger.info(f"Бонус для реферала {res.ref_tg_id} уже был предоставлен. Повторное предоставление бонуса не разрешено.")
    #             return
    #         client.expiry_time += 5 * 86400 * 1000
    #         res.expired += timedelta(days=5)
    #         ref.bonus_given = True
    #         await self.session.commit()
    #         await api.inbound.update(self.client.inbound.id, self.client.inbound)
        