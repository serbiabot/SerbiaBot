import requests
from bs4 import BeautifulSoup

from db import enums
from db.models import SearchOption
from parsers.BaseParser import BaseParser
from parsers.sendler import MessageContext


class NekretnineParser(BaseParser):

    def __init__(self, chat_id, page=1):
        super().__init__(chat_id, page)
        self.site_url = 'https://www.nekretnine.rs'

    async def send_request(self):
        link = await self.build_link()
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            offers = soup.find_all(class_='row offer')
            clean_data = []

            for element in offers:
                img = element.find('img').get('data-src')
                link = self.site_url + element.find('a').get('href')
                price = element.find(class_='offer-price').get_text().split('€')[0]
                area = element.find(class_='offer-price offer-price--invert').get_text().split(' ')[0]
                date_and_rooms = element.find(class_='mt-1 mt-lg-2 mb-lg-0 d-md-block offer-meta-info offer-adress').get_text().split('|')

                clean_data.append(
                    MessageContext(
                        image_url=img,
                        link=link,
                        price=int(price.replace(" ",  "")),
                        area=float(area),
                        rooms=NekretnineAdapter('not need').decode_rooms(date_and_rooms[2]),
                        date=date_and_rooms[0].replace(" ", "").replace("\n", ""),
                    ).return_dict()
                )

            return clean_data

    async def build_link(self):
        options: SearchOption = self.user.search_options
        real_estate_type = '/stambeni-objekti/stanovi' if options.real_estate_type in \
            [enums.RealEstate.RU_APARTMENT, enums.RealEstate.EN_APARTMENT] else '/stambeni-objekti/kuce' + '/izdavanje-prodaja/prodaja'
        city = '/grad/' + NekretnineAdapter(options).get_city_value()
        condition = NekretnineAdapter(options).get_condition()
        areas = f'/kvadratura/{options.min_area}_{options.max_area}'
        price = f'/cena/{options.min_price}_{options.max_price}'
        rooms = f'/ukupan-broj-soba/' + NekretnineAdapter(options).get_rooms_value()
        pagination = f'/po-stranici/20/'
        page = f'stranica/{self.page}/'
        order_by = '?order=2'
        return self.site_url + real_estate_type + city + condition + areas + price + rooms + pagination + page + order_by


class NekretnineAdapter:
    def __init__(self, options):
        self.options = options

    def get_city_value(self):
        if self.options.city in [enums.Cities.EN_BELGRAD, enums.Cities.RU_BELGRAD]:
            return 'beograd'
        elif self.options.city in [enums.Cities.EN_VALEVO, enums.Cities.RU_VALEVO]:
            return 'valjevo'
        elif self.options.city in [enums.Cities.EN_VRNACHKA, enums.Cities.RU_VRNACHKA]:
            return 'vrnjacka-banja'
        elif self.options.city in [enums.Cities.EN_ZRENYANIN, enums.Cities.RU_ZRENYANIN]:
            return 'zrenjanin'
        elif self.options.city in [enums.Cities.EN_LOZNICA, enums.Cities.RU_LOZNICA]:
            return 'loznica-macvanski'
        elif self.options.city in [enums.Cities.EN_KRALEVO, enums.Cities.RU_KRALEVO]:
            return 'kraljevo'
        elif self.options.city in [enums.Cities.EN_KRAGUEVAC, enums.Cities.RU_KRAGUEVAC]:
            return 'kragujevac'
        elif self.options.city in [enums.Cities.EN_NISH, enums.Cities.RU_NISH]:
            return 'nis'
        elif self.options.city in [enums.Cities.EN_NOVI_SAD, enums.Cities.RU_NOVI_SAD]:
            return 'novi-sad'
        elif self.options.city in [enums.Cities.EN_PANCHEVO, enums.Cities.RU_PANCHEVO]:
            return 'pancevo'
        elif self.options.city in [enums.Cities.EN_PIROT, enums.Cities.RU_PIROT]:
            return 'pirot'
        elif self.options.city in [enums.Cities.EN_SOMBOR, enums.Cities.RU_SOMBOR]:
            return 'sombor'
        elif self.options.city in [enums.Cities.EN_SUBOTICA, enums.Cities.RU_SUBOTICA]:
            return 'subotica'
        elif self.options.city in [enums.Cities.EN_UZHICE, enums.Cities.RU_UZHICE]:
            return 'uzice-zlatiborski'
        elif self.options.city in [enums.Cities.EN_CHACHAK, enums.Cities.RU_CHACHAK]:
            return 'cacak'
        elif self.options.city in [enums.Cities.EN_SHABAC, enums.Cities.RU_SHABAC]:
            return 'sabac'
        elif self.options.city in [enums.Cities.EN_JAGODINA, enums.Cities.RU_JAGODINA]:
            return 'jagodina'
        else:
            return None

    def get_rooms_value(self):
        if self.options.rooms in [enums.Rooms.APART_1, enums.Rooms.HOUSE_1]:
            return '1_1'
        elif self.options.rooms in [enums.Rooms.APART_1_2, enums.Rooms.HOUSE_1_2]:
            return '1_2'
        elif self.options.rooms in [enums.Rooms.APART_2]:
            return '2_2'
        elif self.options.rooms in [enums.Rooms.APART_3_4, enums.Rooms.HOUSE_3_4]:
            return '3_4'
        elif self.options.rooms in [enums.Rooms.APART_4_PLUS, enums.Rooms.HOUSE_4_PLUS]:
            return '4_6'
        elif self.options.rooms in [enums.Rooms.APART_STUDIO]:
            return '0_1'
        return '1_2'

    def get_condition(self):
        if self.options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
            return '/stanje-objekta/novogradnja_u-izgradnji'
        elif self.options.rooms in [enums.PropertyCondition.RU_OLD, enums.PropertyCondition.EN_OLD]:
            return '/stanje-objekta/u-izgradnji_standardna-gradnja'
        else:
            return ''

    def decode_rooms(self, text):
        text = text.strip()

        if text == "Garsonjera":
            return '0.5'
        elif text == "Jednosoban stan":
            return '1'
        elif text == "Dvosoban stan":
            return '2'
        elif text == "Trosoban stan":
            return '3'
        elif text == "Četvorosoban stan":
            return '4'
        elif text == "Petosoban+ stan":
            return '5+'

        return text
