from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from db import enums
from db.models import SearchOption
from utils.general import filtered_enum, get_user, filtered_room_enum


async def kb_menu(data):
    language, row = data['language'], []
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    text = 'Добро пожаловать в главное меню 💁‍♀️' if language == enums.Language.Ru else 'Welcome to main menu 💁‍♀️'
    for enum_item in filtered_enum(enums.Menu, language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    return markup, text


async def kb_languages(lang=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    text = 'Выберите язык' if lang == enums.OptionsMenu.RU_LANGUAGE.value else 'Choose language'
    but1 = KeyboardButton('Русский 🇷🇺')
    but2 = KeyboardButton('English 🇬🇧')
    markup.row(but1, but2)
    return markup, text


async def kb_cities(data):
    language, row = data['language'], []
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    text = 'Выберите город 🏨' if language == enums.Language.Ru else 'Choose city 🏨'
    for enum_item in filtered_enum(enums.Cities, language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    return markup, text


async def kb_rooms(data):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    language, row = data['language'], []
    text = 'Выберите количество комнат' if language == enums.Language.Ru else 'Choose numbers of rooms'
    for enum_item in filtered_room_enum(enums.Rooms, data['home_type']):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    return markup, text


async def kb_price_type(data):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    language, row = data['language'], []
    text = 'Выберите цену для редактирования' if language == enums.Language.Ru else 'Choose type of price'
    for enum_item in filtered_enum(enums.PriceType, language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    markup.row(KeyboardButton('назад' if language == enums.Language.Ru else 'back'))
    return markup, text


async def kb_price(data):
    markup = ReplyKeyboardMarkup()
    language = data['language']

    if 'min_price' not in data:
        text = '💶 От какой суммы искать недвижимость (полная стоимость)? (€)' if language == enums.Language.Ru \
            else '💶 From what amount to look for real estate? (€)'
        return markup, text
    if 'max_price' not in data:
        text = '💶 До какой суммы искать недвижимость? (€)' if language == enums.Language.Ru \
            else '💶 Up to what amount to look for real estate? (€)'
        return markup, text


async def kb_price_m2(data):
    markup = ReplyKeyboardMarkup()
    language = data['language']

    if 'min_price_m2' not in data:
        text = '💶📐 Укажите минимальную цену за м2? (€)' if language == enums.Language.Ru \
            else '💶📐 Specify the minimum price per m2? (€)'
        return markup, text
    if 'max_price_m2' not in data:
        text = '💶📐 Укажите максимальную цену за м2? (€)' if language == enums.Language.Ru \
            else '💶📐 Specify the maximum price per m2? (€)'
        return markup, text


async def kb_area(data):
    markup = ReplyKeyboardMarkup()
    language = data['language']

    if 'min_area' not in data:
        text = 'Введите минимальную площадь 📐 в m2' \
            if language == enums.Language.Ru else 'Enter the minimum area 📐 in m2'
        return markup, text
    if 'max_area' not in data:
        text = 'Введите максимальную площадь 📐' if language == enums.Language.Ru.value \
            else 'Enter the maximum areas 📐'
        return markup, text


async def kb_home_type(data):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    language, row = data['language'], []
    text = 'Выберите тип недвижимости 🏡' if language == enums.Language.Ru else 'Choose a property type 🏡'
    for enum_item in filtered_enum(enums.RealEstate, language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    return markup, text


async def kb_condition(data):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    language, row = data['language'], []
    text = 'Выберите состояние жилья' if language == enums.Language.Ru else 'Choose condition of property'
    for enum_item in filtered_enum(enums.PropertyCondition, language):
        row.append(KeyboardButton(enum_item.value))
    markup.row(*row)
    return markup, text


async def kb_auth_menu(user):
    markup, row = ReplyKeyboardMarkup(resize_keyboard=True), []
    text = 'Добро пожаловать в главное меню' if user.language == enums.Language.Ru else 'Welcome to main menu'
    Enum = enums.Menu if user.renew_data else enums.MenuContinue
    for enum_item in filtered_enum(Enum, user.language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    return markup, text


async def kb_options_menu(user):
    option: SearchOption = get_user(user.chat_id).search_options
    markup, row = ReplyKeyboardMarkup(resize_keyboard=True), []
    RU = True if user.language == enums.Language.Ru else False

    text = [
        '⚙️ Ваши параметры',
        f'*язык*: {user.language}',
        f'{option.city}, {option.real_estate_type}, {option.rooms}-комн.',
        f'• Цена:  `{option.min_price}-{option.max_price}` €',
        f'• Цена\м2:  `{option.min_price_m2}-{option.max_price_m2}` €\m2',
        f'• Площадь:  `{option.min_area}-{option.max_area}` m2',
        f'• Состояние жилья: {option.condition}',
        f'Уведомления: включены 🔔' if user.notifications else 'Уведомления: выключены 🔕'
    ] if user.language == enums.Language.Ru else [
        '⚙️ Your parametrs',
        f'*language*: {user.language}',
        f'{option.city}, {option.real_estate_type}, {option.rooms}-rooms',
        f'• Price:  `{option.min_price}-{option.max_price}` €',
        f'• Price\м2:  `{option.min_price_m2}-{option.max_price_m2}` €\m2',
        f'• Areas:  `{option.min_area}-{option.max_area}` m2',
        f'• Property condition: {option.condition}',
        f'*Notifications*: on 🔔' if user.notifications else '*Notifications*: off 🔕'
    ]

    for enum_item in filtered_enum(enums.OptionsMenu, user.language):
        row.append(KeyboardButton(enum_item.value))
        if len(row) == 2:
            markup.row(*row)
            row = []
    markup.row(KeyboardButton('справка' if RU else 'note'), KeyboardButton('назад' if RU else 'back'))
    return markup, text


async def kb_admin():
    set_adv_button = KeyboardButton(enums.AdminPanel.RU_SET_ADVERTISING.value)
    see_adv_button = KeyboardButton(enums.AdminPanel.RU_SEE_ADVERTISING.value)
    button_back = KeyboardButton('назад')
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(set_adv_button)
    markup.add(see_adv_button)
    markup.add(button_back)
    return markup
