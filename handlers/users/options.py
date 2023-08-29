from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db import enums
from handlers.users.registration import registration_dp as dp
from keyboards import reply
from states import options
from utils import general as utils
from utils.general import switch_language, get_user, init_auth, change_user_field


@dp.message_handler(
    Text(equals=[enums.Menu.RU_OPTIONS.value, enums.Menu.EN_OPTIONS.value]),
)
async def bot_options_menu(message: types.Message):
    user = await utils.init_auth(message.chat.id)
    if user:
        markup, text = await reply.kb_options_menu(user)
        await message.answer(text='\n'.join(text), reply_markup=markup, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_LANGUAGE.value, enums.OptionsMenu.RU_LANGUAGE.value]),
)
async def select_language(message: types.Message):
    if await init_auth(message.chat.id):
        markup, text = await reply.kb_languages(lang=message.text)
        await message.answer(text=text, reply_markup=markup)
        await options.LanguageChanger.Change.set()


@dp.message_handler(
    Text(equals=[i.value for i in enums.Language]),
    state=options.LanguageChanger
)
async def change_language(message: types.Message, state: FSMContext):
    option = get_user(message.chat.id).search_options
    await utils.change_user_field(
        message.chat.id,
        'language',
        message.text
    )
    await utils.change_option_field(
        message.chat.id,
        'city',
        switch_language(option.city.value, enums.Cities, lang=message.text)
    )
    await utils.change_option_field(
        message.chat.id,
        'real_estate_type',
        switch_language(option.real_estate_type.value, enums.RealEstate, lang=message.text)
    )
    await utils.change_option_field(
        message.chat.id,
        'condition',
        switch_language(option.condition, enums.PropertyCondition, lang=message.text)
    )
    await utils.bot_menu_after_renew(message)
    await state.finish()


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.RU_CONDITION.value, enums.OptionsMenu.EN_CONDITION.value]),
)
async def select_condition(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:
        markup, text = await reply.kb_condition({'language': user.language})
        await message.answer(text=text, reply_markup=markup)
        await options.ConditionChanger.Change.set()


@dp.message_handler(
    Text(equals=[i.value for i in enums.PropertyCondition]),
    state=options.ConditionChanger.Change
)
async def change_condition(message: types.Message, state: FSMContext):
    await utils.change_option_field(message.chat.id, 'condition', message.text)
    await change_user_field(message.chat.id, 'renew_data', True)
    await utils.bot_menu_after_renew(message)
    await state.finish()


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_CITY.value, enums.OptionsMenu.RU_CITY.value]),
)
async def select_city(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:
        markup, text = await reply.kb_cities({'language':  user.language})
        await message.answer(text=text, reply_markup=markup)
        await options.CityChanger.Change.set()


@dp.message_handler(
    Text(equals=[i.value for i in enums.Cities]),
    state=options.CityChanger.Change
)
async def change_city(message: types.Message, state: FSMContext):
    await utils.change_option_field(message.chat.id, 'city', message.text)
    await change_user_field(message.chat.id, 'renew_data', True)
    await utils.bot_menu_after_renew(message)
    await state.finish()


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_HOME_TYPE.value, enums.OptionsMenu.RU_HOME_TYPE.value]),
)
async def select_real_estate_type(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:
        markup, text = await reply.kb_home_type({'language':  user.language})
        await message.answer(text=text, reply_markup=markup)
        await options.RealEstateChanger.Change.set()


@dp.message_handler(
    Text(equals=[i.value for i in enums.RealEstate]),
    state=options.RealEstateChanger.Change
)
async def change_real_estate_type(message: types.Message, state: FSMContext):
    await utils.change_option_field(message.chat.id, 'real_estate_type', message.text)
    await change_user_field(message.chat.id, 'renew_data', True)
    await utils.bot_menu_after_renew(message)
    await state.finish()


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_ROOMS.value, enums.OptionsMenu.RU_ROOMS.value]),
)
async def select_rooms(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:
        markup, text = await reply.kb_rooms(
            {
                'language': user.language,
                'home_type': user.search_options.real_estate_type
            }
        )
        await message.answer(text=text, reply_markup=markup)
        await options.RoomChanger.Change.set()


@dp.message_handler(
    Text(equals=[i.value for i in enums.Rooms]),
    state=options.RoomChanger.Change
)
async def change_rooms(message: types.Message, state: FSMContext):
    await utils.change_option_field(message.chat.id, 'rooms', message.text)
    await change_user_field(message.chat.id, 'renew_data', True)
    await utils.bot_menu_after_renew(message)
    await state.finish()


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_AREA.value, enums.OptionsMenu.RU_AREA.value]),
)
async def select_area(message: types.Message):
    user = await utils.init_auth(str(message.chat.id))
    if user:
        text = 'Введите минимальную площадь 📐 в m2' \
            if user.language == enums.Language.Ru else 'Enter the minimum area 📐 in m2'
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
        await options.AreaChanger.Change.set()


@dp.message_handler(
    state=options.AreaChanger.Change
)
async def change_area(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = await utils.init_auth(message.chat.id)
        num = await utils.is_not_numeric(message.text, data, lang=get_user(message.chat.id).language)
        if num:
            return await message.answer(text=num)

        if 'min_area' not in data:
            data['min_area'] = int(message.text)
            text = '📐 Введите максимальную площадь' if user.language == enums.Language.Ru.value \
                else '📐 Enter the maximum areas'
            return await message.answer(text=text)

        if 'max_area' not in data:
            await utils.change_option_field(message.chat.id, 'min_area', int(data['min_area']))
            await utils.change_option_field(message.chat.id, 'max_area', int(message.text))

        data.clear()
        await state.finish()
        await change_user_field(message.chat.id, 'renew_data', True)
        await utils.bot_menu_after_renew(message)
    

@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_PRICE.value, enums.OptionsMenu.RU_PRICE.value]),
)
async def select_price(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:
        markup, text = await reply.kb_price_type({'language': user.language})
        await message.answer(text=text, reply_markup=markup)


@dp.message_handler(
    Text(equals=[i.value for i in enums.PriceType]),
)
async def select_price(message: types.Message):
    user = utils.get_user(message.chat.id)
    if user:

        if message.text in [enums.PriceType.EN_M2_PRICE, enums.PriceType.RU_M2_PRICE]:
            markup, text = await reply.kb_price_m2({'language': user.language})
            await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
            await options.M2PriceChanger.Change.set()
        else:
            markup, text = await reply.kb_price({'language': user.language})
            await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
            await options.FullPriceChanger.Change.set()


@dp.message_handler(
    state=options.FullPriceChanger.Change
)
async def change_full_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = await utils.init_auth(message.chat.id)
        num = await utils.is_not_numeric(message.text, data, lang=user.language)
        if num:
            return await message.answer(text=num)

        if 'min_price' not in data:
            data['min_price'] = int(message.text)
            text = '💶 До какой суммы искать недвижимость? (€)' if user.language == enums.Language.Ru.value \
                  else '💶 Enter the maximum cost in euros'
            return await message.answer(text=text)

        if 'max_price' not in data:
            await utils.change_option_field(message.chat.id, 'min_price', int(data['min_price']))
            await utils.change_option_field(message.chat.id, 'max_price', int(message.text))

        data.clear()
        await state.finish()
        await change_user_field(message.chat.id, 'renew_data', True)
        await utils.bot_menu_after_renew(message)


@dp.message_handler(
    state=options.M2PriceChanger.Change
)
async def change_m2_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = await utils.init_auth(message.chat.id)
        num = await utils.is_not_numeric(message.text, data, lang=user.language)
        if num:
            return await message.answer(text=num)

        if 'min_price_m2' not in data:
            data['min_price_m2'] = int(message.text)
            text = '💶 Максимальная цена за m2? (€)' if user.language == enums.Language.Ru.value \
                  else '💶 Maximum price per m2 in euros'
            return await message.answer(text=text)

        if 'max_price_m2' not in data:
            await utils.change_option_field(message.chat.id, 'min_price_m2', int(data['min_price_m2']))
            await utils.change_option_field(message.chat.id, 'max_price_m2', int(message.text))

        data.clear()
        await state.finish()
        await change_user_field(message.chat.id, 'renew_data', True)
        await utils.bot_menu_after_renew(message)


@dp.message_handler(
    Text(equals=[enums.OptionsMenu.EN_STOP_BOT.value, enums.OptionsMenu.RU_STOP_BOT.value]),
)
async def stop_recommendations(message: types.Message):
    user = await init_auth(message.chat.id)
    if user:
        if user.notifications:
            text = 'Notifications are off ☑️' if message.text == enums.OptionsMenu.EN_STOP_BOT.value \
                else 'Уведомления выключены ☑️'
            user = await change_user_field(message.chat.id, 'notifications', False)
            await message.answer(text=text)
        else:
            text = 'Notifications are on ✅' if message.text == enums.OptionsMenu.EN_STOP_BOT.value \
                else 'Уведомления включены ✅'
            user =await change_user_field(message.chat.id, 'notifications', True)
            await message.answer(text=text)
        markup, text = await reply.kb_options_menu(user)
        markup2, text2 = await reply.kb_auth_menu(user)
        await message.answer(text='\n'.join(text), reply_markup=markup2, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(Text(equals=['справка', 'note']))
async def options_note(message: types.Message):
    await message.answer(
        text=enums.ReminderNote.RU_NOTE.value if message.text == 'справка' else enums.ReminderNote.EN_NOTE.value,
        disable_web_page_preview=True,
    )


option_dp = dp
