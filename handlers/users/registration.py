from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text

from db import enums
from loader import dp
from states.registration import Registration
from keyboards import reply
from utils.general import create_user, is_not_numeric, find_enum_field, get_user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = get_user(message.chat.id)
    if not user:
        markup, _ = await reply.kb_languages()
        await message.answer(text='Какой язык вам наиболее удобен?', reply_markup=markup)
        await Registration.City.set()
    else:
        markup, text = await reply.kb_auth_menu(user)
        await message.answer(text=text, reply_markup=markup)


@dp.message_handler(
    Text(equals=[i.value for i in enums.Language]),
    state=Registration.City,
)
async def bot_choose_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['language'] = enums.Language.Ru if message.text == enums.Language.Ru else enums.Language.En
        markup, text = await reply.kb_cities(data)
        await message.answer(text=text, reply_markup=markup)
        await Registration.next()


@dp.message_handler(
    Text(equals=[i.value for i in enums.Cities]),
    state=Registration.HomeType,
)
async def bot_choose_home_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
        markup, text = await reply.kb_home_type(data)
        await message.answer(text=text, reply_markup=markup)
        await Registration.next()


@dp.message_handler(
    Text(equals=[i.value for i in enums.RealEstate]),
    state=Registration.Condition,
)
async def bot_choose_condition(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['home_type'] = find_enum_field(enums.RealEstate, message.text)
        markup, text = await reply.kb_condition(data)
        await message.answer(text=text, reply_markup=markup)
        await Registration.next()


@dp.message_handler(
    Text(equals=[i.value for i in enums.PropertyCondition]),
    state=Registration.Room,
)
async def bot_choose_rooms(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['condition'] = message.text
        markup, text = await reply.kb_rooms(data)
        await message.answer(text=text, reply_markup=markup)
        await Registration.next()


@dp.message_handler(
    Text(equals=[i.value for i in enums.Rooms]),
    state=Registration.Price,
)
async def bot_choose_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['rooms'] = message.text
        markup, text = await reply.kb_price(data)
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
        await Registration.next()


@dp.message_handler(
    state=Registration.Area,
)
async def bot_choose_areas(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        num = await is_not_numeric(message.text, data, lang=data['language'])
        if num:
            return await message.answer(text=num)

        if 'min_price' not in data:
            data['min_price'] = int(message.text)
            markup, text = await reply.kb_price(data)
            return await message.answer(text=text, reply_markup=None)

        if 'max_price' not in data:
            data['max_price'] = int(message.text)
            markup, text = await reply.kb_area(data)
            await Registration.next()
            return await message.answer(text=text, reply_markup=markup)

        markup, text = await reply.kb_price(data)
        await message.answer(text=text, reply_markup=None)


@dp.message_handler(
    state=Registration.Menu,
)
async def bot_send_menu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        num = await is_not_numeric(message.text, data, lang=data['language'])
        if num:
            return await message.answer(text=num)

        if 'min_area' not in data:
            data['min_area'] = int(message.text)
            markup, text = await reply.kb_area(data)
            return await message.answer(text=text, reply_markup=None)

        if 'max_area' not in data:
            data['max_area'] = int(message.text)
            markup, text = await reply.kb_menu(data)
            await create_user(data, message.chat.id)
            await message.answer(text=text, reply_markup=markup)
            data.clear()
            return await state.finish()

        markup, text = await reply.kb_area(data)
        await message.answer(text=text, reply_markup=None)


registration_dp = dp
