from py3xui import Api, AsyncApi, Inbound, Client
from db.engine import AsyncSessionMaker
from uuid import uuid4
import  qrcode
from sqlalchemy import select
from datetime import datetime, timedelta, timezone, time
from db.models import User, Subscription
import time
import os
api = AsyncApi(
    host='https://94.183.186.146:55591/cwb9fj6JhB8r8EIlNY/',
    username='JUHEyo8TCy',
    password='u9LnAKdP6Y'
)


inbound = None



async def startup():
    global inbound
    await api.login()
    inbounds = await api.inbound.get_list()
    inbound = inbounds[0]

    





async def add_client(tg_id: int, days: int):
    global inbound

    expired = datetime.fromtimestamp(
    days / 1000,
    tz=timezone.utc
)
    if inbound is None:
        raise RuntimeError("inbound НЕ инициализирован (startup не вызывался)")


    new_client = Client(id=str(uuid4()), enable=True, email=str(tg_id), expiryTime=days, flow='xtls-rprx-vision')
    public_key = inbound.stream_settings.reality_settings.get('settings').get('publicKey')
    website_name = inbound.stream_settings.reality_settings.get('serverNames')[0]
    sid_name = inbound.stream_settings.reality_settings.get('shortIds')[0]
    key = f'vless://{new_client.id}@94.183.186.146:443?type=tcp&encryption=none&security=reality&pbk={public_key}&fp=chrome&sni={website_name}&sid={sid_name}&spx=%2F&flow={new_client.flow}#dw-{new_client.email}'
    
    async with AsyncSessionMaker() as session:
        user = await session.scalar(select(User).
                                  where(User.telegram_id == tg_id))

        if not user:
            user = User(telegram_id=tg_id, reg_date=datetime.now())
            session.add(user)
            await session.flush()
            session.add(Subscription(status='active', expired=expired, user_id=user.id, uuid=new_client.id, key=key, subs_tg_id=tg_id))
            await session.commit()
            inbound.settings.clients.append(new_client)
            await api.inbound.update(inbound.id, inbound)
            
        


async def change_client(price, tg_id):
    global inbound
    async with AsyncSessionMaker() as session: 
        stmt = await session.scalars(select(Subscription).where(tg_id == Subscription.subs_tg_id))
        res = stmt.one_or_none()
        
        
        
        existing_client = inbound.settings.clients[res.id]
        print(existing_client, 'Данные')
        

        now = datetime.now()
        
        print(res.uuid)
        if res.expired < now and existing_client.id == res.uuid:
            res.expired = now + timedelta(days=price)
            existing_client.expiry_time = int((time.time() + price * 86400) * 1000)
            
        if res.expired >= now and existing_client.id == res.uuid:
            expiredd = price * 86000 * 1000
            res.expired += timedelta(days=price)
            existing_client.expiry_time += expiredd
        await api.inbound.update(inbound.id, inbound)
        await session.commit()




         