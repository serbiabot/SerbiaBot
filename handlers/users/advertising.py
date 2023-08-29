from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from db import enums

from db.config import ADMINS
from keyboards import reply
from loader import dp
from utils.general import get_user, create_advertisement
from states.options import AdminMenu
from jobs.jobs import send_advertising_notifications


@dp.message_handler(commands=['admin'])
async def admin_menu(message: types.Message):
    user = get_user(message.chat.id)
    if user and user.chat_id in ADMINS:
        text = 'Что необходимо сделать?'
        markup = await reply.kb_admin()
        await message.answer(text=text, reply_markup=markup)
    else:
        await message.answer(text='Доступ запрещен')


@dp.message_handler(
    Text(equals=[option.value for option in enums.AdminPanel]),
)
async def select_option(message: types.Message, state: FSMContext):
    user = get_user(message.chat.id)
    if user and user.chat_id in ADMINS:
        if message.text == enums.AdminPanel.RU_SET_ADVERTISING.value:
            text = 'Пришлите рекламный текст'
            await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
            prompt = """В тексте рекламы допускается делать разметку.
                Небольшая справка по часто используемому синтаксису:
                1️⃣ \*реклама\* - будет выглядеть как   *реклама*
                2️⃣ \_реклама\_ - будет выглядеть как   _реклама_
                3️⃣ \[реклама](https://www.youtube.com/) - будет выглядеть как [реклама](https://www.youtube.com/),
                 нажав на которую, можно перейти по ссылке"""
            await message.answer(text=prompt, disable_web_page_preview=True)
            await AdminMenu.Advertising_text.set()
        elif message.text == enums.AdminPanel.RU_SEE_ADVERTISING.value:
            await send_advertising_notifications(admin=message.chat.id)


@dp.message_handler(
    content_types=types.ContentTypes.TEXT,
    state=AdminMenu.Advertising_text
)
async def input_advertising_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        await message.answer(text='Текст заменен')
        await message.answer(text='Пришлите рекламное изображение. Если изображение '
                                  'в объявлении не предусмотрено, ответьте любым текстовым сообщением')
        await AdminMenu.next()


@dp.message_handler(
    content_types=types.ContentTypes.PHOTO | types.ContentTypes.TEXT,
    state=AdminMenu.Advertising_image
)
async def input_advertising_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1]['file_id'] if message.photo else ''
        await create_advertisement(data)
        await state.finish()
        markup = await reply.kb_admin()
        text = 'Рекламное объявление изменено!'
        await message.answer(text=text, reply_markup=markup)
