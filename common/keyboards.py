from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder




def inl():
    kb = InlineKeyboardBuilder()
    kb.button(text='Купить/Продлить💳', callback_data='buyvpn')
    kb.button(text='История покупок🛍️', callback_data='history_shop')
    kb.button(text='Мой VPN📲', callback_data='my_prof_vpn')
    kb.button(text='Инструкция📖', callback_data='instructions')
    kb.button(text='Реферальная система', callback_data='referal')
    kb.button(text='Поддержка🛠️', callback_data='support', url='https://t.me/mdjabrailov')
    kb.adjust(1)
    return kb


intsr = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android📱', callback_data='android')],
    [InlineKeyboardButton(text='IOS📱', callback_data='iphone')],
    [InlineKeyboardButton(text='Windows / Mac💻', callback_data='windows')],
    [InlineKeyboardButton(text='TV 🖥', callback_data='tv')],
    [InlineKeyboardButton(text='🏠Меню', callback_data='main_menu')]
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

def res():
    rp = ReplyKeyboardBuilder()
    rp.button(text='restart')
    rp.adjust(1)
    return rp

def admin_panel():
    kb = InlineKeyboardBuilder()
    kb.button(text='📊 Статистика', callback_data='static_users')
    kb.button(text='VPN-операции', callback_data='vpn_operations')
    kb.button(text='Рассылка', callback_data='mailing')
    kb.button(text='Назад', callback_data='main_menu')
    kb.adjust(1)
    return kb

def back_inst():
    kb = InlineKeyboardBuilder()
    kb.button(text='⬅Назад', callback_data='back_instr')
    kb.adjust(1)
    return kb

def vpn_operations():
    kb = InlineKeyboardBuilder()
    kb.button(text='Продление подписки по Telegram ID', callback_data='extension_sub')
    kb.button(text='Удалить пользователя по Telegram ID', callback_data='delete_user')
    kb.adjust(1)
    return kb

def mailing_butt():
    kb = InlineKeyboardBuilder()
    kb.button(text='Истекает на днях', callback_data='expir_days')
    kb.button(text='Осталось больше 7 дн', callback_data='more_sev_day')
    return kb

