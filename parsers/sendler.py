from enum import Enum

from aiogram import types

from db import enums
from jobs.utils import clean_jobs
from keyboards import reply
from loader import bot
from utils.general import get_user, bot_send_notification, change_user_field, collect_parsers


class ParserHub:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.is_send = False

    async def logic_of_all_parsers(self, page=1, renew=False):
        await clean_jobs(self.chat_id) if renew else None
        await change_user_field(self.chat_id, 'renew_data', False)
        await change_user_field(self.chat_id, 'notifications', True)
        user = get_user(self.chat_id)
        parsers = await collect_parsers(user.search_options)

        for parser in parsers:
            try:
                check_send = await parser(self.chat_id, page=page).parse(silent=self.is_send, renew=renew)
                self.is_send = True if (check_send or self.is_send) else False
                renew = False
            except Exception as e:
                pass

        if not self.is_send:
            text = enums.Notifications.RU_EMPTY_PARSE.value if user.language == enums.Language.Ru \
                else enums.Notifications.EN_EMPTY_PARSE.value
            return await bot_send_notification(self.chat_id, text=text)

    async def send_batch(self, user, json_data, count=4):
        markup, _ = await reply.kb_auth_menu(user)
        len_data = len(json_data)
        if count > len_data >= 1:
            count = len_data
        if len_data >= count:
            for record in range(count):
                announcement = json_data[record]
                text = await MessageBuilder(
                    user.language,
                    user.search_options,
                    json_data=announcement
                ).build_message()

                try:
                    await bot.send_photo(
                        user.chat_id,
                        announcement['image_url'],
                        caption='\n'.join(text),
                        parse_mode=types.ParseMode.MARKDOWN,
                        reply_markup=markup
                    )
                except Exception as e:
                    pass

            return json_data[count:]
        else:
            pass


class MessageContext:
    def __init__(self, link=None, image_url=None, street=None, price=None, each_price=None,
                 floor=None, area=None, date=None, rooms=None, **kwargs):
        self.link = link
        self.image_url = image_url
        self.street = street
        self.price = price
        self.each_price = each_price
        self.floor = floor
        self.area = area
        self.date = date
        self.rooms = rooms

        for key, value in kwargs.items():
            setattr(self, key, value)

    def return_dict(self):
        context_dict = {
            "link": self.link,
            "image_url": self.image_url,
            "street": self.street,
            "price": self.price,
            "floor": self.floor,
            "area": self.area,
            "rooms": self.rooms,
            "date": self.date
        }

        for key, value in vars(self).items():
            if key not in context_dict:
                context_dict[key] = value

        return context_dict


class MessageBuilder:

    class Titles(str, Enum):
        EN_CITY = 'City'
        RU_CITY = 'Город'
        EN_PRICE = "Price"
        RU_PRICE = "Цена"
        EN_STREET = 'Street'
        RU_STREET = 'Улица'
        EN_DATE = 'Размещено'
        RU_DATE = 'Размещено'
        EN_FLOOR = 'Floor'
        RU_FLOOR = 'Этаж'

    def __init__(self, language, options, json_data):
        self.language = language
        self.options = options
        self.data = json_data

    async def build_message(self):
        RU = True if self.language == enums.Language.Ru else False
        room_prefix = 'комн.' if RU else 'rooms'
        city_prefix = 'Город:' if RU else 'City:'
        link_prefix = 'ссылка на объявление' if RU else 'link to the ad'
        price_prefix = 'Цена:' if RU else 'Price'
        data_prefix = 'Размещение:' if RU else 'Date:'

        street = f", {self.data['street']} st." if self.data['street'] != None else ""
        room = f" {self.data['rooms'] if self.data['rooms'] != None else self.options.rooms}-{room_prefix}"
        area = f", {self.data['area']} m²" if self.data['area'] != None else ""

        text = [
            f"[{link_prefix}]({self.data['link']})",
            f"{city_prefix} *{self.options.city}*" + street,
            f"{self.options.real_estate_type}" + room + area,
        ]

        if self.data['date']:
            text.append(f"{data_prefix} {self.data['date']}",)

        if self.data['price']:
            text.append(f"{price_prefix} {self.data['price']}  €")
        elif self.data['each_price']:
            text.append(f"{price_prefix} {self.data['each_price']}")
        else:
            text.append(f"{price_prefix} {'договорная' if RU else 'negotiated'} ")

        return text
