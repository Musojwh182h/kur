from aiogram import F, Router
from db.engine import AsyncSessionMaker
from ServiceClasses.user_service import UserService
from ServiceClasses.shoping_service import ShopingService
from aiogram.types import CallbackQuery
import logging
logger = logging.getLogger(__name__)

history_router = Router()

@history_router.callback_query(F.data == 'history_shop')
async def history_shoping(callback: CallbackQuery):
     async with AsyncSessionMaker() as session:
        user = UserService(session)
        shoping = ShopingService(session)
        user_id = await user.check_user(callback.from_user.id)
        if not user_id:
             await callback.message.answer('Попробуйте заново нажав /start')
             return
        shops = await shoping.get_shoping(user_id)
        if not shops:
               await callback.message.answer('У вас пока нету покупок')
               logger.info(f"Пользователь {callback.from_user.id} запросил историю покупок, но покупок не найдено.")
               return
        for shop in shops:
            shop_date_str = shop.shop_date.strftime('%d.%m.%Y %H:%M') if shop.shop_date else '—'
            text = f'''
Куплено в {shop_date_str}.
Потрачено {shop.money} Р.'''
            await callback.message.answer(text)