import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db import enums
from db.database import redis_get, redis_save
from jobs.utils import append_parsers_data
from keyboards import reply
from parsers.sendler import ParserHub
from utils.general import init_auth, change_user_field, get_user, bot_send_notification
from handlers.users.options import option_dp as dp


@dp.message_handler(Text(equals=[enums.Menu.EN_SEARCH.value, enums.Menu.RU_SEARCH.value]))
async def bot_search(message: types.Message):
    if await init_auth(message.chat.id):
        await change_user_field(message.chat.id, 'notifications', True)
        await message.answer('Идет подбор вариантов...' if message.text == enums.Menu.RU_SEARCH.value \
            else 'There is a selection of options...')
        await ParserHub(message.chat.id).logic_of_all_parsers(renew=True)


@dp.message_handler(Text(equals=[enums.MenuContinue.EN_SEARCH.value, enums.MenuContinue.RU_SEARCH.value]))
async def bot_search_continue(message: types.Message):
    user = get_user(message.chat.id)
    json_data = redis_get(message.chat.id)
    if await init_auth(message.chat.id):
        if json_data:
            json_data = await ParserHub(message.chat.id).send_batch(user, json_data, count=3)
            redis_save(message.chat.id, json_data)
        else:
            text = enums.Notifications.RU_EMPTY_PARSE.value if user.language == enums.Language.Ru \
                else enums.Notifications.EN_EMPTY_PARSE.value
            await append_parsers_data(user)
            return await bot_send_notification(message.chat.id, text=text)


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    user = await init_auth(message.chat.id)
    if user:
        markup, text = await reply.kb_auth_menu(user)
        await message.answer(text=text, reply_markup=markup)


@dp.message_handler(lambda message: message.text != '/admin', state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    user = get_user(message.chat.id)
    async with state.proxy() as data:
        text = "Choose an item from the proposed menu 💁‍♀️" if user and user.language == enums.Language.En \
            else "Выберите пункт из предложенного меню 💁‍♀️"

        data.setdefault('count', 1)
        data['count'] += 1

        if data['count'] == 5:
            await state.finish()
            return await message.answer('State is closed. try /menu 👈 menu')

    await message.answer(text=text)

search_dp = dp
