from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder



inl = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Купить/Продлить💳', callback_data='buyvpn')],
    [InlineKeyboardButton(text='Мой VPN📲', callback_data='my_prof_vpn')],
    [InlineKeyboardButton(text='Инструкция📖', callback_data='instructions')],
    [InlineKeyboardButton(text='Поддержка🛠️', callback_data='support', url='https://t.me/mdjabrailov')]

])

intsr = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android📱', callback_data='android')],
    [InlineKeyboardButton(text='IOS📱', callback_data='iphone')],
    [InlineKeyboardButton(text='Windows 💻', callback_data='wimdows')],
    [InlineKeyboardButton(text='macOS 💻', callback_data='macos')],
    [InlineKeyboardButton(text='TV 🖥', callback_data='tv')]
])




def inline_times():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f'1 мес. - 149Р️', callback_data='time_1')
    keyboard.button(text=f'3 мес. - 299Р️', callback_data='time_3')
    keyboard.button(text=f'6 мес. - 649Р️', callback_data='time_6')
    keyboard.button(text=f'12 мес. - 999Р️', callback_data='time_12')
    keyboard.button(text='⬅Назад', callback_data='main_menu')
    keyboard.adjust(2)
    return keyboard.as_markup()

buy_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅Назад', callback_data='back')]
    ])

