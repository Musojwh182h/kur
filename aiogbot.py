import asyncio
import os
from py3xui import AsyncApi
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notification import notifications
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
from ServiceClasses.vpn_service import VPNService
from common.handlers_flder.start_cmd import start_router
from common.handlers_flder.history_shops import history_router
from common.handlers_flder.admin import admin_router
from common.handlers_flder.instructions import instr_router
from common.handlers_flder.main_menu import main_router
from common.handlers_flder.my_vpn import my_vpn_router
from common.handlers_flder.puy_vpn import puy_router

from common.handlers_flder.referal_system import referal_router
from common.handlers_flder.reset import handler_router
from common.handlers_flder.time_vpn import time_router
from common.usr_cmnds import private
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  
        logging.StreamHandler()           
    ]
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(history_router)
dp.include_router(instr_router)
dp.include_router(main_router)
dp.include_router(my_vpn_router)
dp.include_router(puy_router)
dp.include_router(admin_router)
dp.include_router(referal_router)
dp.include_router(time_router)
dp.include_router(handler_router)


        


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    scheduler.add_job(
        notifications, 
        'cron',
        hour=12,
        minute=0,
        args=[bot]
    )
    scheduler.start()
    await dp.start_polling(bot)
    
asyncio.run(main())

