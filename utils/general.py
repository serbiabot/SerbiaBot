from aiogram import types
from sqlalchemy.orm import sessionmaker, joinedload

from db import enums
from db.config import engine
from db.models import User, SearchOption, Advertisement
from keyboards import reply
from loader import bot


async def init_auth(
    chat_id,
    session=sessionmaker(bind=engine)()
):
    user = session.query(User).filter(User.chat_id == str(chat_id)).first()
    session.close()
    if user:
        return user
    await bot.send_message(chat_id, '/start  👈 to register ')
    return


def get_user(chat_id, session=sessionmaker(bind=engine)()):
    user = session.query(User).filter(User.chat_id == str(chat_id)).options(
        joinedload(User.search_options)).first()
    session.close()
    if user:
        return user
    return None


async def create_user(data, chat_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    option = SearchOption(
        city=data['city'],
        rooms=data['rooms'],
        real_estate_type=data['home_type'],
        condition=data['condition'],
        min_price=data['min_price'],
        max_price=data['max_price'],
        min_price_m2=1000,
        max_price_m2=6000,
        min_area=data['min_area'],
        max_area=data['max_area'],
    )

    new_user = User(
        chat_id=str(chat_id),
        language=data['language'],
        search_options=option

    )

    session.add_all([option, new_user])
    session.commit()
    session.close()


async def is_not_numeric(input_str, data=None, lang=None):
    try:
        float(input_str)
    except ValueError:
        return 'Ошибочное\не число' if lang == enums.Language.Ru else \
            'wrong or not number'

    if float(input_str) < 0:
        return 'Число должно быть не меньше 0' if lang == enums.Language.Ru else \
            ' Integer must be >= 0'

    if 'min_price' in data and 'max_price' not in data:
        if float(data['min_price']) > float(input_str):
            return 'Максимальное число должно быть больше минимального' if lang == enums.Language.Ru else \
                'The maximum number must be greater than the minimum'
    if 'min_area' in data:
        if float(data['min_area']) > float(input_str):
            return 'Максимальное число должно быть больше минимального' if lang == enums.Language.Ru else \
                'The maximum number must be greater than the minimum'
    return False


def filtered_enum(Enum, filter):
    if filter == enums.Language.Ru:
        return [item for item in Enum if item.name.startswith("RU_")]
    else:
        return [item for item in Enum if item.name.startswith("EN_")]


def filtered_room_enum(Enum, filter):
    if filter in [enums.RealEstate.RU_HOUSE, enums.RealEstate.EN_HOUSE]:
        return [item for item in Enum if item.name.startswith("HOUSE_")]
    else:
        return [item for item in Enum if item.name.startswith("APART_")]


def find_enum_field(Enum, search_string):
    for enum_item in Enum:
        if enum_item.value == search_string:
            return enum_item
    return


async def change_user_field(chat_id, field, value):
    session = sessionmaker(bind=engine)()
    session.expire_on_commit = False
    user = session.query(User).filter_by(chat_id=str(chat_id)).first()

    setattr(user, field, value)

    session.commit()
    session.close()
    return user


async def change_option_field(chat_id, field, value):
    session = sessionmaker(bind=engine)()
    session.expire_on_commit = False
    user = get_user(chat_id)
    search_option = user.search_options

    setattr(search_option, field, value)

    session.add(search_option)
    session.commit()
    session.close()
    return user


def get_enum_item(value, Enum):
    try:
        return Enum.__members__[value]
    except KeyError:
        return None


def switch_language(text, Enum, lang):
    if text in [item.value for item in Enum]:
        opposite_language = 'RU' if lang == enums.Language.Ru.value else 'EN'
        for item in Enum:
            if item.value == text:
                opposite = opposite_language + item.name[2:]
                return get_enum_item(opposite, Enum)


async def bot_send_notification(chat_id, text):
    try:
        await bot.send_message(
            chat_id,
            text=text,
            parse_mode=types.ParseMode.MARKDOWN
        )
    except:
        pass


async def bot_menu_after_renew(message):
    user = await init_auth(message.chat.id)
    await change_user_field(message.chat.id, 'notifications', False)
    if user:
        markup, text = await reply.kb_options_menu(user)
        markup2, text2 = await reply.kb_auth_menu(user)
        await message.answer(text='\n'.join(text), reply_markup=markup2, parse_mode=types.ParseMode.MARKDOWN)


async def create_advertisement(data):
    session = sessionmaker(bind=engine)()
    text, photo = data.values()

    advertisement = session.query(Advertisement).first()
    if advertisement:
        advertisement.description = text
        advertisement.image = photo if photo else None
    else:
        advertisement = Advertisement(description=text, image=photo) if photo else Advertisement(description=text)
        session.add(advertisement)

    session.commit()
    session.close()


async def collect_parsers(options):
    from parsers.sites.cityexpert import CityExpertParser
    from parsers.sites.novazgrada import NovazGradaParser
    from parsers.sites.nekretnine import NekretnineParser
    from parsers.sites.halooglasi import HalooglasiParser
    from parsers.sites.zida4 import FourZidaParser

    parsers = [
        FourZidaParser,
        NekretnineParser,
        # HalooglasiParser,
    ]

    if (options.city in [enums.Cities.RU_NISH, enums.Cities.EN_NISH, enums.Cities.RU_NOVI_SAD,
        enums.Cities.EN_NOVI_SAD, enums.Cities.EN_BELGRAD, enums.Cities.RU_BELGRAD]):
        parsers.append(CityExpertParser)
    if options.condition in [enums.PropertyCondition.RU_NEW, enums.PropertyCondition.EN_NEW] and \
            options.city in [enums.Cities.RU_BELGRAD, enums.Cities.EN_BELGRAD] and \
            options.real_estate_type in [enums.RealEstate.RU_APARTMENT, enums.RealEstate.EN_APARTMENT]:
        parsers.append(NovazGradaParser)

    return parsers
