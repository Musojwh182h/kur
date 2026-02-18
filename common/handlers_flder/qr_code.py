# from aiogram import F, Router, Bot
# from aiogram.types import CallbackQuery, BufferedInputFile
# from db.engine import AsyncSessionMaker
# from ServiceClasses.vpn_service import VPNService
# from ServiceClasses.subscription_service import SubscrService
# from py3xui import AsyncApi
# from dotenv import load_dotenv
# import os
# load_dotenv() 
# import logging
# import qrcode
# from io import BytesIO

# logger = logging.getLogger(__name__)




# qr_code_router = Router()

# @qr_code_router.callback_query(F.data == 'qr_code')
# async def qr_code_image(callback: CallbackQuery, bot: Bot):
#     try:
#         async with AsyncSessionMaker() as session:
#             sub  = SubscrService(session)
#             vpn = VPNService(session)
#             sub = await sub.get_sub(callback.from_user.id)
#             if not sub:
#                 await callback.message.answer('У вас нет активной подписки. Пожалуйста, приобретите её или нажмите /start чтобы увидеть детали.')
#                 logger.info(f'Пользователь {callback.from_user.id} попытался просмотреть QR-код без активной подписки.')
#                 return
#             img = qrcode.make(sub.key)
#             buffer = BytesIO()
#             img.save(buffer, format='PNG')
#             photo = BufferedInputFile(buffer.getvalue(), filename='qr.png')
#             await callback.message.answer_photo(photo, caption='Отсканируйте QR-код, чтобы подключится')
#     except Exception:
#                  await callback.message.answer('Чтобы продолжить, нажмите /start')
#                  return
    