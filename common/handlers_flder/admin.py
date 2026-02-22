from aiogram.filters import CommandStart, CommandObject
from aiogram import F, Bot
from aiogram.types import CallbackQuery
from ServiceClasses.admin_panel_service import AdminPanel
import logging
from dotenv import load_dotenv
import os
load_dotenv() 
from db.engine import AsyncSessionMaker
import asyncio
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from aiogram.types import Message
from aiogram.enums import ParseMode
from common.keyboards import inl, admin_panel as admin_panel_kb, vpn_operations, mailing_butt
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

logger = logging.getLogger(__name__)

class Admin(StatesGroup):
    search_user = State()

class Extension(StatesGroup):
    exten_user = State()
    days_count = State()

class Delete_User(StatesGroup):
    del_use = State()

class GiveVpn(StatesGroup):
    give = State()

class MailAct(StatesGroup):
    act = State()

class MailInact(StatesGroup):
    inact = State()


admin_router = Router()

admin = os.getenv('ADMIN').split(',')

@admin_router.callback_query(F.data == 'admin')
async def admin_panel(callback: CallbackQuery):
    await callback.message.answer('Вы в админ панели:', reply_markup=admin_panel_kb().as_markup())

@admin_router.callback_query(F.data == 'static_users')
async def static_use(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text='Статистика пользователя', callback_data='static_one_user')
    kb.button(text='Статистика всех пользователей', callback_data='all_static_users')
    kb.adjust(1)
    await callback.message.answer('Выберите просмотр статистики: ', reply_markup=kb.as_markup())

@admin_router.callback_query(F.data == 'static_one_user')
async def static_one(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.search_user)
    await callback.message.answer('Введите айди пользователя, которого хотите посмотреть статистику: ')

@admin_router.message(Admin.search_user)
async def search_use(message: Message, state: FSMContext):
    async with AsyncSessionMaker() as session:
        try:
            await state.update_data(search_user=int(message.text))
        except ValueError:
            await message.answer('Введите айди пользователя числом')
            return
        data = await state.get_data()
        st_member = AdminPanel(session)
        st_member = await st_member.users_search(data['search_user'])
        if not st_member:
            await message.answer('Пользователь не найден или нет данных')
            await state.clear()
            return
        await message.answer(str(st_member))
        await state.clear()

@admin_router.callback_query(F.data == 'all_static_users')
async def static_all_users(callback: CallbackQuery):
    async with AsyncSessionMaker() as session:
        st_member = AdminPanel(session)
        st_member = await st_member.static_users()
        if not st_member:
            await callback.message.answer('В боте нет ни одного пользователя')
            return
        await callback.message.answer(st_member)

@admin_router.callback_query(F.data == 'vpn_operations')
async def vpn_oper(callback: CallbackQuery):
    await callback.message.answer('Выберите что хотите сделать с пользователем: ', reply_markup=vpn_operations().as_markup())



@admin_router.callback_query(F.data == 'extension_sub')
async def sub_extension(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Extension.exten_user)
    await callback.message.answer('Введите айди пользователя, которого хотите продлить поодписку: ')



@admin_router.message(Extension.exten_user)
async def fsm_exten(message: Message, state: FSMContext):
    try:
        await state.update_data(exten_user=int(message.text))
    except ValueError:
            await message.answer('Введите айди пользователя числом')
            return
    await state.set_state(Extension.days_count)
    await message.answer('Введите на сколько дней хотите продлить (например: ' \
'10)')
    
@admin_router.message(Extension.days_count)
async def fsm_days(message: Message, state: FSMContext):
    try:
        await state.update_data(days_count=int(message.text))
    except ValueError:
            await message.answer('Введите дни числом')
            return
    data = await state.get_data()
    async with AsyncSessionMaker() as session:
        admin = AdminPanel(session)
        admin = await admin.upd_vpn(data['exten_user'], data['days_count'])
        if not admin:
            await message.answer('Пользователь не найден или нет данных')
            await state.clear()
            return
        await message.answer('Пользователь успешно продлен!')
        await state.clear()


@admin_router.callback_query(F.data == 'delete_user')
async def user_del(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Delete_User.del_use)
    await callback.message.answer('Введите айди пользователя, которого хотите удалить профиль: ')



@admin_router.message(Delete_User.del_use)
async def fsm_del(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(del_use=int(message.text))
    except ValueError:
            await message.answer('Введите айди пользователя числом')
            return
    data = await state.get_data()
    async with AsyncSessionMaker() as session:
        if data['del_use'] == message.from_user.id:
            await message.answer('Нельзя удалить самого себя!')
            await state.clear()
            return
        if not data['del_use']:
            await message.answer('Пользователь не найден')
            await state.clear()
            return
        admin = AdminPanel(session)
        admin = await admin.del_users(data['del_use'])
        await message.answer('Пользователь успешно удален!')
        await bot.send_message(chat_id=data['del_use'], text='Вы и все ваши данные удалены за нарушение. Если не согласны, напишите в поддержку')
        await state.clear()

@admin_router.callback_query(F.data == 'mailing')
async def mailings(callback: CallbackQuery):
    await callback.message.answer('Сделать рассылку тем у кого: ', reply_markup=mailing_butt().as_markup())


@admin_router.callback_query(F.data == 'expir_days')
async def mail_expir(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.set_state(MailAct.act)
    await callback.message.answer('Напишите то, что хотели бы разослать: ')
    

@admin_router.message(MailAct.act)
async def fsm_act(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(act=message.text)
    data = await state.get_data()
    async with AsyncSessionMaker() as session:
            admin = AdminPanel(session)
            admin = await admin.mailing_act()
            if not admin:
                await message.answer('Таких пользователей нет')
                return await state.clear()
            for i in admin:
                try:
                    await bot.send_message(chat_id=i.vpn_tg_id, text=data['act'])  
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    try:
                        await bot.send_message(chat_id=i.vpn_tg_id, text=data['act'])
                    except TelegramForbiddenError:
                        continue
                except Exception:
                    continue  
    await state.clear()
    await message.answer('Рассылка отправлена')

@admin_router.callback_query(F.data == 'more_sev_day')
async def mail_more_sev(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MailInact.inact)
    await callback.message.answer('Напишите то, что хотели бы разослать: ')


@admin_router.message(MailInact.inact)
async def fsm_inact(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(inact=message.text)
    data = await state.get_data()
    async with AsyncSessionMaker() as session:
            admin = AdminPanel(session)
            admin = await admin.mailing_inact()
            if not admin:
                await message.answer('Таких пользователей нет')
                return await state.clear()
            for i in admin:
                try:
                    await bot.send_message(chat_id=i.vpn_tg_id, text=data['inact'])    
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    try:
                        await bot.send_message(chat_id=i.vpn_tg_id, text=data['inact']) 
                    except TelegramForbiddenError:
                        continue
                except TelegramForbiddenError:
                    continue
    await state.clear()
    await message.answer('Рассылка отправлена')