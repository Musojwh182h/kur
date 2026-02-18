from common.text_handlers import text, photo_path
from aiogram.filters import CommandStart, CommandObject

from ServiceClasses.subscription_service import SubscrService
from ServiceClasses.user_service import UserService
from ServiceClasses.vpn_service import VPNService
from ServiceClasses.referal_service import RerferalService
import logging
from dotenv import load_dotenv
import os
load_dotenv() 
from db.engine import AsyncSessionMaker
from aiogram.types import Message
from aiogram.enums import ParseMode
from common.keyboards import inl
from aiogram import Router
from aiogram import types

logger = logging.getLogger(__name__)



start_router = Router()

@start_router.message(CommandStart())
async def start_cmd(message: Message, command: CommandObject):
    try:
        tg_user = message.from_user.id
        async with AsyncSessionMaker() as session:
            user = UserService(session)
            client = VPNService(session)
            sub = SubscrService(session)
            ref = RerferalService(session, client)
            user_id = await user.check_user(tg_user)
            if not user_id:
                await user.create_user(tg_user)
                logger.info(f"Пользователь с Telegram ID {tg_user} создан в базе данных.")
                await client.create_client(tg_user)                                                                                                                                                                                                                                                                     
                await sub.create_sub(tg_user)
                logger.info(f"Подписка создана для пользователя: {tg_user}")
            if command.args:
                try:
                    value = command.args.split()
                    invited_id = int(value[0])
                except (ValueError, IndexError):
                    await message.answer('Неправильная ссылка')
                    logger.warning(f"Такая ссылка не правильная: {command.args} от пользователя: {tg_user}")
                    return
                
                if tg_user != invited_id:
                    check_user = await user.check_user(invited_id)                
                    if not check_user:
                        logger.warning(f'Такой пригласивший пользователь не найден: {invited_id} для приглашающего пользователя: {tg_user}')
                        return None
                    await ref.create_referal(tg_user, invited_id)
                    logger.info(f'Создан реферал для пользователя: {tg_user} приглашённым пользователем: {invited_id}')
                    ref_tg = await ref.get_referal(tg_user)
                    sub_tg = await sub.get_sub(invited_id)
                    if ref_tg and not ref_tg.bonus_given:
                        await client.referal_vpn(invited_id, ref_tg)
                        logger.info(f'Реферальный бонус применён для пользователя: {invited_id} за приглашённого пользователя: {tg_user}')
                        await user.referal_count_(ref_tg.invited_by_tg_id)      
                    else:
                        return None
    
    
    
        await message.answer_photo(
            photo=types.FSInputFile(
                path=photo_path
            ),
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=inl
        )

    except Exception:
        await message.answer('Произошла неизвестная ошибка, перезайдите в бота по позже')
        logger.exception('На стороне клиента Произошла неизвестная ошибка')
        return
