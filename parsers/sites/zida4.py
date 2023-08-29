import re
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

from db import enums
from db.models import SearchOption
from parsers.BaseParser import BaseParser
from parsers.sendler import MessageContext


class FourZidaParser(BaseParser):
    """
    We are parsing this site thanks to XHR queries that
    found in the developer console.
    We receive data from the internal API of the api.4zida.rs

    P.S. weak point: the site has a homemade encoding of the
    query parameter dictionary in the get parameters (it may change)
    """

    def __init__(self, chat_id, page=1):
        super().__init__(chat_id, page)
        self.site_url = 'https://api.4zida.rs'

    async def send_request(self):
        link = await self.build_link()
        request = requests.get(link)
        clean_data = []

        if request.status_code == 200:
            RU = True if self.user.language == enums.Language.Ru else False
            if self.user.search_options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
                soup = BeautifulSoup(request.text, 'html.parser')
                offers = soup.find_all(class_='relative pb-12 drop-shadow-md bg-white rounded-4zida overflow-hidden mb-2')
                clean_data = []

                for element in offers:

                    img = element.find('img').get('şrc')
                    link = element.find('a').get('href')
                    street_and_areas = element.find('p', class_='px-3 pb-3 text-sm').text.replace('\n', '')
                    matches = re.findall(r'[0-9\s]+', element.find('p', class_='px-3 pb-3 text-orange-500 text-xl font-bold').text)
                    price = ''.join(matches).replace(' ', '').replace('\n', '')
                    price = f'{"до" if RU else "to"} {price} €' if price else ('договорная' if RU else 'negotiated')

                    clean_data.append(
                        MessageContext(
                            image_url=img,
                            link=link,
                            each_price=price,
                            area=street_and_areas.split("m2")[0].strip(),
                        ).return_dict()
                    )

                return clean_data

            else:
                response = request.json()['ads']

                for jsn in response:
                    try:
                        clean_data.append(
                            MessageContext(
                                image_url=jsn['image']['search']['380x0_fill_0_webp'],
                                link='https://4zida.rs' + jsn['urlPath'],
                                street=jsn['address'] if 'address' in jsn else None,
                                price=jsn['price'],
                                area=jsn['m2'],
                                rooms=jsn["roomCount"] if "roomCount" in jsn else None,
                            ).return_dict()
                        )
                    except:
                        pass

                return clean_data

    async def build_link(self):
        options: SearchOption = self.user.search_options
        if options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
            return f'https://www.4zida.rs/novogradnja/?rooms=&priceTo={options.max_price}&sizeFrom={options.min_area}&sortBy=Sortiraj'
        else:
            prefix = 'houses' if (options.real_estate_type in [enums.RealEstate.EN_HOUSE, enums.RealEstate.RU_HOUSE]) else 'apartments'
            params = {
                "for": "sale",
                "priceFrom": options.min_price,
                "priceTo": options.max_price,
                "page": self.page,
                "m2From": options.min_area,
                "m2To": options.max_area,
                "placeIds[]": [FourZidaAdapter(options).get_city_value()],
                "structures[]": FourZidaAdapter(options).get_rooms_value(),
                "states[]": FourZidaAdapter(options).get_condition_value(),
                # "showPerPage": "",
            }
            return self.site_url + "/v7/search/" + prefix + "?" + urlencode(params, doseq=True)


class FourZidaAdapter:
    def __init__(self, options):
        self.options = options

    def get_city_value(self):
        if self.options.city in [enums.Cities.EN_BELGRAD, enums.Cities.RU_BELGRAD]:
            return 2
        elif self.options.city in [enums.Cities.EN_VALEVO, enums.Cities.RU_VALEVO]:
            return 1961
        elif self.options.city in [enums.Cities.EN_VRNACHKA, enums.Cities.RU_VRNACHKA]:
            return 4325
        elif self.options.city in [enums.Cities.EN_ZRENYANIN, enums.Cities.RU_ZRENYANIN]:
            return 1184
        elif self.options.city in [enums.Cities.EN_LOZNICA, enums.Cities.RU_LOZNICA]:
            return 28654
        elif self.options.city in [enums.Cities.EN_KRALEVO, enums.Cities.RU_KRALEVO]:
            return 4055
        elif self.options.city in [enums.Cities.EN_KRAGUEVAC, enums.Cities.RU_KRAGUEVAC]:
            return 8031
        elif self.options.city in [enums.Cities.EN_NISH, enums.Cities.RU_NISH]:
            return 8036
        elif self.options.city in [enums.Cities.EN_NOVI_SAD, enums.Cities.RU_NOVI_SAD]:
            return 28073
        elif self.options.city in [enums.Cities.EN_PANCHEVO, enums.Cities.RU_PANCHEVO]:
            return 1254
        elif self.options.city in [enums.Cities.EN_PIROT, enums.Cities.RU_PIROT]:
            return 5499
        elif self.options.city in [enums.Cities.EN_SOMBOR, enums.Cities.RU_SOMBOR]:
            return 1017
        elif self.options.city in [enums.Cities.EN_SUBOTICA, enums.Cities.RU_SUBOTICA]:
            return 1053
        elif self.options.city in [enums.Cities.EN_UZHICE, enums.Cities.RU_UZHICE]:
            return 3565
        elif self.options.city in [enums.Cities.EN_CHACHAK, enums.Cities.RU_CHACHAK]:
            return 3676
        elif self.options.city in [enums.Cities.EN_SHABAC, enums.Cities.RU_SHABAC]:
            return 1696
        elif self.options.city in [enums.Cities.EN_JAGODINA, enums.Cities.RU_JAGODINA]:
            return 2535
        else:
            return None

    def get_rooms_value(self):
        rooms = []

        if self.options.rooms in [enums.Rooms.APART_STUDIO]:
            rooms.append(101)
        if self.options.rooms in [enums.Rooms.APART_1, enums.Rooms.APART_1_2]:
            rooms.append(102)
            rooms.append(103)
            rooms.append(104)
        if self.options.rooms in [enums.Rooms.APART_2, enums.Rooms.APART_1_2]:
            rooms.append(105)
            rooms.append(106)
        if self.options.rooms in [enums.Rooms.APART_3_4]:
            rooms.append(106)
            rooms.append(107)
        if self.options.rooms in [enums.Rooms.APART_4_PLUS]:
            rooms.append(145)
        return rooms

    def get_condition_value(self):
        condition = []
        if self.options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
            condition.append("new")
        if self.options.condition in [enums.PropertyCondition.EN_OLD, enums.PropertyCondition.RU_OLD]:
            condition.append("original")
        return condition
