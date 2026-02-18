import logging
logger = logging.getLogger(__name__)
from db.models import Vpn_Account, User
import os
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from dotenv import find_dotenv, load_dotenv
from remnawave import RemnawaveSDK
from remnawave.models.users import CreateUserRequestDto, UpdateUserRequestDto
from remnawave.exceptions import ConflictError

load_dotenv(find_dotenv())

REMNAWAVE_BASE_URL = os.getenv("PANEL_URL")
REMNAWAVE_TOKEN = os.getenv("API_TOKEN")
REMNAWAVE_INTERNAL_SQUAD_UUID = os.getenv("REMNAWAVE_INTERNAL_SQUAD_UUID")

if not REMNAWAVE_BASE_URL or not REMNAWAVE_TOKEN:
    raise RuntimeError(
        "Не заданы PANEL_URL/API_TOKEN."
    )
rem = RemnawaveSDK(base_url=REMNAWAVE_BASE_URL, token=REMNAWAVE_TOKEN)

class VPNService: 
    def __init__(self, session):
        self.rem = rem
        self.session = session

    async def create_client(self, tg):
        username = str(tg)
        expire_date = datetime.now(UTC) + timedelta(days=3)

        active_internal_squads = None
        if REMNAWAVE_INTERNAL_SQUAD_UUID:
            active_internal_squads = [REMNAWAVE_INTERNAL_SQUAD_UUID]

        create_body = CreateUserRequestDto(
            username=username,
            expire_at=expire_date,
            telegram_id=tg,
            active_internal_squads=active_internal_squads,
        )
        try:
            rem_user = await self.rem.users.create_user(create_body)
        except ConflictError:
            rem_user = await self.rem.users.get_user_by_username(username)

        if not rem_user:
            logger.warning('Такого клиента нету')
            return

        subscription = await self.rem.subscriptions.get_subscription_by_uuid(str(rem_user.uuid))

        db_user = await self.session.scalar(select(User).where(User.telegram_id == tg))
        if not db_user:
            raise RuntimeError(f"Пользователь с tg_id={tg} не найден в БД")

        vpn_account = await self.session.scalar(
            select(Vpn_Account).where(Vpn_Account.user_id == db_user.id)
        )
        if vpn_account:
            vpn_account.uuid = str(rem_user.uuid)
            vpn_account.expired_at = rem_user.expire_at
            vpn_account.key = subscription.subscription_url
        else:
            vpn_account = Vpn_Account(
                uuid=str(rem_user.uuid),
                expired_at=rem_user.expire_at,
                key=subscription.subscription_url,
                user_id=db_user.id,
            )
            self.session.add(vpn_account)

        await self.session.commit()
        
        
        

    
    async def get_vpn_subscription(self, tg_id):
        user = await self.session.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            logger.warning(f"Пользователь с tg_id={tg_id} не найден в БД")
            return
        vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
        if not vpn:
            logger.warning('такого клиента нету')
            return
        subscription = await self.rem.subscriptions.get_subscription_by_uuid(str(vpn.uuid))
        return subscription.subscription_url
    
    async def get_vpn_account(self, tg):
        user = await self.session.scalar(select(User).where(User.telegram_id == tg))
        if not user:
            logger.warning('такого клиента нету')
            return
        vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
        if not vpn:
            logger.warning('такого клиента нету')
            return
        return vpn
    
    async def buy_vpn(self, tg_id, days):
        user = await self.session.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            logger.warning('такого клиента нету')
            return
        vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
        if not vpn:
            logger.warning('у пользователя нету впн')
            return

        vpn_exp = await self.rem.users.get_user_by_uuid(str(vpn.uuid))
        now = datetime.now(UTC)
        expired = vpn_exp.expire_at or now

        if expired < now:
            new_date = now + timedelta(days=days)
        else:
            new_date = expired + timedelta(days=days)

        body = UpdateUserRequestDto(uuid=vpn_exp.uuid, expire_at=new_date)
        updated = await self.rem.users.update_user(body)

        vpn.expired_at = updated.expire_at
        await self.session.commit()
        return updated.expire_at
    
    async def referal_vpn(self, invited, tg_user):
        user = await self.session.scalar(select(User).where(User.telegram_id == invited))
        if not user:
            logger.warning('такого клиента нету')
            return
        vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
        if not vpn:
            logger.warning('у пользователя нету впн')
            return
        vpn_exp = await self.rem.users.get_user_by_uuid(str(vpn.uuid))
        now = datetime.now(UTC)
        expired = vpn_exp.expire_at or now
        if tg_user.bonus_given == True:
            logger.info(f"Бонус для пользователя {invited} уже был предоставлен. Повторное предоставление бонуса не разрешено.")
            return
        body = UpdateUserRequestDto(uuid=vpn_exp.uuid, expire_at=expired + timedelta(days=5))
        updated = await self.rem.users.update_user(body)
        vpn.expired_at = updated.expire_at
        tg_user.bonus_given = True
        await self.session.commit()
