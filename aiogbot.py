import asyncio
import os
from py3x import startup
from aiogram import Bot, Dispatcher, types
from db.models import User, Subscription
from datetime import datetime,  timedelta
from sqlalchemy.engine import URL
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.util import await_only
from sqlalchemy import select
from db.engine import AsyncSessionMaker
load_dotenv(find_dotenv())

from common.handler import handler_router
from common.usr_cmnds import private
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Сохранять в файл
        logging.StreamHandler()           # +Показывать в консоли
    ]
)

logger = logging.getLogger(__name__)


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(handler_router)
# async def notification(bot: Bot):
#     now = datetime.now()
#     while True:
#         now = datetime.now()
#         async with AsyncSessionMaker() as session:
#             sub = await session.scalars(select(Subscription))
#             for s in sub:
#                 delta = s.expired - now
#                 if 1 <= delta.days < 2:
#                     await bot.send_message(s.subs_tg_id, 'Срок вашей подписки подходит к концу, продлите чтобы продолжить пользоваться KUR-VPN!')
#                 if 0 <= delta.days <= 1:
#                     await bot.send_message(s.subs_tg_id, 'Срок вашей подписки подходит к концу, продлите чтобы продолжить пользоваться KUR-VPN!')
#         await asyncio.sleep(86400)
        


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await startup()
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # asyncio.create_task(notification(bot))
    await dp.start_polling(bot)
    
asyncio.run(main())

