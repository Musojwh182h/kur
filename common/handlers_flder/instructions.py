from aiogram import Router, F
from aiogram.types import CallbackQuery
from common.keyboards import intsr, back_inst
instr_router = Router()
from aiogram.enums import ParseMode


@instr_router.callback_query(F.data =='instructions')
async def instr(callback: CallbackQuery):
    await callback.message.answer('Выерите устройство: ', reply_markup=intsr)

@instr_router.callback_query(F.data == 'android')
async def andr(callback: CallbackQuery):
    await callback.message.edit_text('''🤖 Инструкция для Android

🔑 1. Купите ключ

📦 2. Установите приложение:
<a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">V2RayTun в Google Play</a>

📲 3. Скопируйте ключ и вставьте через + → «Добавить из буфера»

⚙️ 4. Разрешите создание VPN-соединения

▶️ 5. Нажмите кнопку подключения — VPN начнёт работать''', reply_markup=back_inst().as_markup(), parse_mode='HTML', disable_web_page_preview=True)
    

@instr_router.callback_query(F.data == 'iphone')
async def andr(callback: CallbackQuery):
    await callback.message.edit_text('''📱 Инструкция для iPhone

🔑 1. Купите ключ

📦 2. Скачайте приложение:
<a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">V2RayTun в App Store</a>

📲 3. Скопируйте ключ и вставьте в приложение через + → «Добавить из буфера»

⚙️ 4. Разрешите создание VPN-соединения

▶️ 5. Нажмите кнопку включения — VPN начнёт работать''', reply_markup=back_inst().as_markup(), parse_mode='HTML', disable_web_page_preview=True)
    

@instr_router.callback_query(F.data == 'tv')
async def andr(callback: CallbackQuery):
    await callback.message.edit_text('''📺 Инструкция для TV

🔑 1. Купите ключ

📦 2. Установите приложение:
<a href="https://play.google.com/store/apps/details?id=com.vpn4tv.hiddify">VPN4TV в Google Play</a>

📲 3. Введите ключ или отсканируйте QR-код

▶️ 4. Подключитесь к VPN''', reply_markup=back_inst().as_markup(), parse_mode='HTML', disable_web_page_preview=True)
    
@instr_router.callback_query(F.data == 'windows')
async def andr(callback: CallbackQuery):
    await callback.message.edit_text('''💻 Инструкция для ПК (Windows/Mac)

🔑 1. Купите ключ

📦 2. Скачайте Hiddify Next:
<a href="https://hiddify.com/">Скачать Hiddify</a>

🛠 3. Установите приложение

🖥️ 4. Скопируйте ключ, нажмите + → «Добавить из буфера обмена»

🌐 5. Нажмите «Подключиться» — VPN активируется''', reply_markup=back_inst().as_markup(), parse_mode='HTML', disable_web_page_preview=True)

@instr_router.callback_query(F.data == 'back_instr')
async def instr_back(callback: CallbackQuery):
    await callback.message.edit_text('Выберите устройство: ', reply_markup=intsr)