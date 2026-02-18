from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from common.text_handlers import time_hendlers
from common.keyboards import inline_times



class Buy(StatesGroup):
    buy = State()

time_router = Router()

@time_router.callback_query(F.data == 'buyvpn')
async def traffic(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Отлично! Выберите тариф, чтобы продолжить: 📦', reply_markup=inline_times())

@time_router.callback_query(F.data.startswith("time_"))
async def time_choice(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text='Оплатить', callback_data='puy')
    kb.button(text='Назад', callback_data='back')
    kb.adjust(1)
    time_butt = int(callback.data.split('_')[1])
    price = {1:149, 3:350, 6:600, 12:999}
    
    await state.update_data(price=int(time_butt))
    await state.set_state(Buy.buy) 
    await callback.answer()
    await callback.message.edit_text(time_hendlers(price, time_butt), reply_markup=kb.as_markup())

@time_router.callback_query(F.data == 'back')
async def back_ck(callback: CallbackQuery):
    await callback.message.edit_text('Отлично! Выберите тариф, чтобы продолжить: 📦', reply_markup=inline_times())

