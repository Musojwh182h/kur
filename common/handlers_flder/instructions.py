from aiogram import Router, F
from aiogram.types import CallbackQuery
from common.keyboards import intsr
instr_router = Router()



@instr_router.callback_query(F.data =='instructions')
async def instr(callback: CallbackQuery):
    await callback.message.edit_text('Выерите устройство: ', reply_markup=intsr)
