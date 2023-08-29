import requests
from bs4 import BeautifulSoup

from db import enums
from db.models import SearchOption
from parsers.BaseParser import BaseParser
from parsers.sendler import MessageContext


class HalooglasiParser(BaseParser):

    def __init__(self, chat_id, page=1):
        super().__init__(chat_id, page)
        self.site_url = 'https://www.halooglasi.com'

    async def send_request(self):
        link = await self.build_link()
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            offers = soup.find_all(class_='product-item product-list-item Premium real-estates my-product-placeholder')
            clean_data = []

            for element in offers:
                img = element.find('img').get('src')
                link = self.site_url + element.find('a').get('href')
                price = element.find(class_='central-feature').get_text().replace("\n", "").split("€")[0].strip()
                date = element.find(class_='publish-date').get_text().replace("\n", "").strip()
                area_rooms = element.find_all(class_='value-wrapper')
                area = area_rooms[0].get_text().split("m2")[0]
                rooms = area_rooms[1].get_text().split(" ")[0]

                clean_data.append(
                    MessageContext(
                        image_url=img,
                        link=link,
                        price=price,
                        area=area,
                        rooms=rooms,
                        date=date,
                    ).return_dict()
                )

            return clean_data

    async def build_link(self):
        options: SearchOption = self.user.search_options
        main_prefix = f"{self.site_url}/nekretnine"
        home_type = "/prodaja-" + ("kuca" if options.real_estate_type in [enums.RealEstate.RU_HOUSE, enums.RealEstate.EN_HOUSE] else "stanova")
        city = f'/{HalooglasiAdapter(options).get_city_value()}?'
        price = f'cena_d_from={options.min_price}&cena_d_to={options.max_price}&cena_d_unit=4'
        area = f'&kvadratura_d_from={options.min_area}&kvadratura_d_to={options.max_area}&kvadratura_d_unit=1'
        rooms = f'&broj_soba_order_i_from={HalooglasiAdapter(options).get_rooms_value()[0]}&broj_soba_order_i_to={HalooglasiAdapter(options).get_rooms_value()[1]}'
        condition = f'&tip_objekta_id_l={HalooglasiAdapter(options).get_condition()}'
        page = f'&page={self.page}'
        return main_prefix + home_type + city + price + area + rooms + condition + page


class HalooglasiAdapter:
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
            return 'loznica'
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
            return [2, 4]
        if self.options.rooms in [enums.Rooms.APART_1_2, enums.Rooms.HOUSE_1_2]:
            return [2, 7]
        elif self.options.rooms in [enums.Rooms.APART_2]:
            return [5, 7]
        elif self.options.rooms in [enums.Rooms.APART_3_4, enums.Rooms.HOUSE_3_4]:
            return [8, 10]
        elif self.options.rooms in [enums.Rooms.APART_4_PLUS, enums.Rooms.HOUSE_4_PLUS]:
            return [9, 12]
        elif self.options.rooms in [enums.Rooms.APART_STUDIO]:
            return [0, 1]
        return [2, 7]

    def get_condition(self):
        if self.options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
            return '387234'
        elif self.options.rooms in [enums.PropertyCondition.RU_OLD, enums.PropertyCondition.EN_OLD]:
            return '387235'
        else:
            return '387234%2C387235'
