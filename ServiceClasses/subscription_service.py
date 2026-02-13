from db.models import User, Subscription, Shoping, Referal
from sqlalchemy import select
from datetime import timedelta, timezone, datetime
import time
import logging
logger = logging.getLogger(__name__)
class SubscrService:
    def __init__(self, session, client):
        self.session = session
        self.client = client
        

    
    
        
    async def create_key(self, client):
        inbound = self.client.inbound
        
        public_key = inbound.stream_settings.reality_settings.get('settings').get('publicKey')
        website_name = inbound.stream_settings.reality_settings.get('serverNames')[0]
        sid_name = inbound.stream_settings.reality_settings.get('shortIds')[0]
        key = f'vless://{client.id}@94.183.186.146:443?type=tcp&encryption=none&security=reality&pbk={public_key}&fp=chrome&sni={website_name}&sid={sid_name}&spx=%2F&flow={client.flow}#dw-{client.email}'
        return key

    async def create_sub(self, days, tg_id, key, client):
        expired = datetime.fromtimestamp(
        days / 1000,
        tz=timezone.utc
    )
        
        user = await self.session.scalar(select(User).where(User.telegram_id == tg_id))
        sub = Subscription(subs_tg_id=tg_id, expired=expired, user_id=user.id, uuid=client.id, key=key)
        self.session.add(sub)
        await self.session.commit()

    async def get_sub(self, tg):
        return await self.session.scalar(select(Subscription).where(Subscription.subs_tg_id == tg))
    
    async def change_client(self, price, tg, api):
    # try:
            sub = await self.get_sub(tg)
            
            if not self.client or not self.client.inbound:
                logger.warning(f"Клиент для пользователя {tg} не найден или не инициализирован. Попытка инициализации клиента.")
                await self.client.startup()
            now = datetime.now()
            try:
                client = None
                for i in self.client.inbound.settings.clients:
                    if i.id == sub.uuid:
                        client = i
                        break
            except Exception as e:
                logger.error(f"Ошибка при поиске клиента для пользователя {tg}: {e}")
                return
                
            
            
            if not sub:
                logger.warning(f"Подписка для пользователя {tg} не найдена. Невозможно изменить клиента.")
                return
            
            if sub.expired < now and client:
                
                sub.expired = now + timedelta(days=price)
                client.expiry_time = int((time.time() + price * 86400) * 1000)
                
            if sub.expired >= now and client:
                expiredd = price * 86400 * 1000
                
                sub.expired += timedelta(days=price)
                client.expiry_time += expiredd
            await api.inbound.update(self.client.inbound.id, self.client.inbound)
            await self.session.commit()

    async def ref_client(self, res, api, ref):
            if not self.client or not self.client.inbound:
                await self.client.startup()
            try:
                client = None
                for i in self.client.inbound.settings.clients:
                    if i.id == res.uuid:
                        client = i
                        break
            except Exception as e:
                logger.error(f"Ошибка при поиске клиента для реферала {res.ref_tg_id}: {e}")   
            if not client:
                logger.warning(f"Клиент для реферала {res.ref_tg_id} не найден. Невозможно применить бонус.")
                return
            if ref.bonus_given == True:
                logger.info(f"Бонус для реферала {res.ref_tg_id} уже был предоставлен. Повторное предоставление бонуса не разрешено.")
                return
            client.expiry_time += 5 * 86400 * 1000
            res.expired += timedelta(days=5)
            ref.bonus_given = True
            await self.session.commit()
            await api.inbound.update(self.client.inbound.id, self.client.inbound)
        