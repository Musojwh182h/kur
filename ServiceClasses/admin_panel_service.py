from db.models import User, Subscription, Vpn_Account, Shoping
from sqlalchemy import select, func, delete
from common.text_handlers import static_user
from datetime import timedelta, datetime, date
import time
import logging
from dotenv import find_dotenv, load_dotenv
from remnawave import RemnawaveSDK
from remnawave.models.users import CreateUserRequestDto, UpdateUserRequestDto
from remnawave.exceptions import ConflictError
import os
load_dotenv(find_dotenv())

REMNAWAVE_BASE_URL = os.getenv("PANEL_URL")
REMNAWAVE_TOKEN = os.getenv("API_TOKEN")
REMNAWAVE_INTERNAL_SQUAD_UUID = os.getenv("REMNAWAVE_INTERNAL_SQUAD_UUID")

if not REMNAWAVE_BASE_URL or not REMNAWAVE_TOKEN:
    raise RuntimeError(
        "Не заданы PANEL_URL/API_TOKEN."
    )
rem = RemnawaveSDK(base_url=REMNAWAVE_BASE_URL, token=REMNAWAVE_TOKEN)


def _safe_now(expire_at):
    if expire_at is not None and expire_at.tzinfo is not None:
        return datetime.now(expire_at.tzinfo)
    return datetime.now()

class AdminPanel:
    def __init__(self, session):
        self.session = session
        self.rem = rem

    async def users_search(self, tg):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg))
            if not user:
                logging.warning('Такого пользователя нету')
                return
            sub = await self.session.scalar(select(Subscription).where(Subscription.user_id == user.id))
            vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
            if not vpn:
                logging.warning('Такого пользователя нету в панели')
                return
            shop = await self.session.scalar(select(func.max(Shoping.shop_date)).where(Shoping.user_id == user.id))
            if not shop:
                logging.warning('Нету покупки')
                
            now = datetime.now()
            days_left = (vpn.expired_at - now).days
            shop_money = await self.session.scalar(select(func.coalesce(func.sum(Shoping.money), 0)).where(Shoping.user_id == user.id))
            shop = await self.session.scalar(select(func.max(Shoping.shop_date)).where(Shoping.user_id == user.id))
            return static_user(user, sub, vpn, days_left, shop, shop_money)
        except Exception as e:
            logging.exception(e)
            return None
        

    async def static_users(self):
        try:
            now = datetime.now()
            today_user = date.today()
            one_week = now - timedelta(days=7)
            one_month = now - timedelta(days=30)
            user_count = await self.session.scalar(select(func.count(User.id)))
            today_count = await self.session.scalar(select(func.count(User.id)).where(func.date(User.reg_date) == today_user))
            one_week_count = await self.session.scalar(select(func.count(User.id)).where(User.reg_date >= one_week))
            one_month_count = await self.session.scalar(select(func.count(User.id)).where(User.reg_date >= one_month))
            sub_active = await self.session.scalar(select(func.count(Subscription.id)).where(Subscription.status == 'active'))
            sub_inactive = await self.session.scalar(select(func.count(Subscription.id)).where(Subscription.status == 'expired'))
            today_shop = await self.session.scalar(select(func.count(Shoping.id)).where(func.date(Shoping.shop_date) == today_user))
            today_shop_money = await self.session.scalar(select(func.coalesce(func.sum(Shoping.money), 0)).where(func.date(Shoping.shop_date) == today_user))
            one_week_shop = await self.session.scalar(select(func.count(Shoping.id)).where(Shoping.shop_date >= one_week))
            one_week_shop_money = await self.session.scalar(select(func.coalesce(func.sum(Shoping.money), 0)).where(Shoping.shop_date >= one_week))
            one_month_shop = await self.session.scalar(select(func.count(Shoping.id)).where(Shoping.shop_date >= one_month))
            one_month_shop_money = await self.session.scalar(select(func.coalesce(func.sum(Shoping.money), 0)).where(Shoping.shop_date >= one_month))
            text = f'''Всего: {user_count if user_count else 'нет пользователей'}
    Новые: сегодня — {today_count if today_count else 'сегодня не было паользователей'}, за 7 дн — {one_week_count if one_week_count else 'на этой недели не было пользователей'}, за 30 дн — {one_month_count if one_month_count else 'за месяц не было новых пользователей'}
    С подпиской: {sub_active if sub_active else 'нет активных подписок'}
    Без подписки/истёкшая: {sub_inactive if sub_inactive else 'нет истекших подписок'}
    Покупки: сегодня - {today_shop if today_shop else 0} / {today_shop_money} ₽  за 7 дн — {one_week_shop if one_week_shop  else 0} / {one_week_shop_money} ₽ за 30 дн — {one_month_shop if one_month_shop  else 0} / {one_month_shop_money} ₽'''
            return text
        except Exception as e:
            logging.exception(e)
            return None
        


    async def upd_vpn(self, tg, exp):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg))
            if not user:
                logging.warning('Такого пользователя нету')
                return
            vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
            if not vpn:
                logging.warning('Такого пользователя нету в панели')
                return
            tm_user = await self.rem.users.get_user_by_uuid(str(vpn.uuid))
            if not tm_user:
                return
            dat = tm_user.expire_at
            now = _safe_now(dat)
            dat = dat or now
            if dat < now:
                new_date = now + timedelta(days=exp)
            else:
                new_date = dat + timedelta(days=exp)
            change_vpn = UpdateUserRequestDto(uuid=tm_user.uuid, expire_at=new_date)
            body = await self.rem.users.update_user(change_vpn)
            vpn.expired_at = body.expire_at
            await self.session.commit()
        except Exception as e:
            logging.exception(e)
            return None

        
    async def del_users(self, tg):
        try:
            user = await self.session.scalar(select(User).where(User.telegram_id == tg))
            if not user:
                logging.warning('Такого пользователя нету')
                return
            vpn = await self.session.scalar(select(Vpn_Account).where(Vpn_Account.user_id == user.id))
            if not vpn:
                logging.warning('Такого пользователя нету в панели')
                return
            
            shop = await self.session.scalar(select(Shoping).where(Shoping.user_id == user.id))
            if not shop:
                logging.warning('Нет покупок')
            tm_user = await self.rem.users.get_user_by_uuid(str(vpn.uuid))
            if tm_user:
                await self.rem.users.delete_user(str(tm_user.uuid))
                await self.session.execute(delete(Vpn_Account).where(Vpn_Account.user_id == user.id))
                await self.session.execute(delete(Subscription).where(Subscription.user_id == user.id))
                await self.session.execute(delete(Shoping).where(Shoping.user_id == user.id))
                await self.session.execute(delete(User).where(User.telegram_id == tg))
                await self.session.commit()
            else:
                return None
        except Exception as e:
            logging.exception(e)
            return None

    async def mailing_act(self):
        try:
            now = datetime.now()
            one_day = now + timedelta(days=1, hours=0, minutes=0, seconds=0)
            three_day = now + timedelta(days=2, hours=23, minutes=59, seconds=59)
            vpn = await self.session.scalars(
                select(Vpn_Account).where(
                    (Vpn_Account.expired_at >= one_day) & (Vpn_Account.expired_at <= three_day)
                )
            ).all()
            if not vpn:
                logging.warning('Такого пользователя нету в панели')
                return
            return vpn
        except Exception as e:
            logging.exception(e)
            return None

        


    async def mailing_inact(self):
        try:
            now = datetime.now()
            one_day = now + timedelta(days=1, hours=0, minutes=0, seconds=0)
            three_day = now + timedelta(days=6, hours=23, minutes=59, seconds=59)
            vpn = await self.session.scalars(
                select(Vpn_Account).where(
                    (Vpn_Account.expired_at >= one_day) & (Vpn_Account.expired_at <= three_day)
                )
            ).all()
            if not vpn:
                logging.warning('Такого пользователя нету в панели')
                return
            return vpn
        except Exception as e:
            logging.exception(e)
            return None