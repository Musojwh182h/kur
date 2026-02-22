from aiogram import Router, types, F
main_router = Router()
from aiogram.types import CallbackQuery
from common.text_handlers import text, photo_path
from common.keyboards import inl
from aiogram.enums import ParseMode




@main_router.callback_query(F.data == 'main_menu')
async def back(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=types.FSInputFile(
            path=photo_path
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=inl().as_markup())
