
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def kb_languages() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    but1 = InlineKeyboardButton('PASS', callback_data='PASS')
    but2 = InlineKeyboardButton('PASS', callback_data='PASS')
    markup.row(but1, but2)
    return markup
