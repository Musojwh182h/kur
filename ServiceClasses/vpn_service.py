from py3xui import  Client
from uuid import uuid4
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, timezone, time
import time
class VPNService:
    def __init__(self, api):
        self.api = api
        self.inbound = None

    async def startup(self):
        await self.api.login()
        inbounds = await self.api.inbound.get_list()
        self.inbound = inbounds[0]
        if self.inbound is None:
                raise RuntimeError("inbound НЕ инициализирован")
           

    async def create_client(self, tg_id, days):
        try:
            client = Client(id=str(uuid4()), enable=True, email=str(tg_id), expiryTime=days, flow='xtls-rprx-vision')
            self.inbound.settings.clients.append(client)
            logger.info(f"Создан VPN клиент для пользователя {tg_id} с истечением через {days} миллисекунд.")
            await self.api.inbound.update(self.inbound.id, self.inbound)
            return client
        except Exception as e:
            logger.error(f"Ошибка при создании VPN клиента для пользователя {tg_id}: {e}")
            raise