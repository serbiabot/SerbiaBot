import json
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from slugify import slugify

from db import enums
from db.models import SearchOption
from parsers.BaseParser import BaseParser
from parsers.sendler import MessageContext


class CityExpertParser(BaseParser):
    """
    We are parsing this site thanks to XHR queries that
    found in the developer console.
    We receive data from the internal API of the cityexpert.rs

    P.S. weak point: the site has a homemade encoding of the
    query parameter dictionary in the get parameters (it may change)
    """

    def __init__(self, chat_id, page=1):
        super().__init__(chat_id, page)
        self.site_url = 'https://cityexpert.rs/api/Search'
        self.site_clean_url = 'https://cityexpert.rs'
        self.img_url = 'https://img.cityexpert.rs/sites/default/files/styles/470x/public/image/'

    async def send_request(self):
        RU = True if self.user.language == enums.Language.Ru else False
        clean_data = []
        if self.user.search_options.condition in [enums.PropertyCondition.EN_NEW, enums.PropertyCondition.RU_NEW]:
            request = requests.get(await self.build_link())
            soup = BeautifulSoup(request.text, 'html.parser')
            offers = soup.find_all(class_='wrap-zgrade-kartica')

            for element in offers:
                try:
                    img = element.find('img').get('src')
                    link = self.site_clean_url + element.find('a').get('href')
                    areas = element.find('div', class_='kvadratura-kartica').text.replace('\n', '')
                    street = element.find('div', class_='adresa-zgrade-kartica').text.replace('\n', '')
                    matches = re.findall(r'[0-9\s]+',
                                         element.find('div', class_='cena-kvadrata-kartica').text)
                    price = ''.join(matches).replace(' ', '').replace('\n', '')
                    price = f'{"от" if RU else "from"} {price} €\m2' if price else ('договорная' if RU else 'negotiated')

                    clean_data.append(
                        MessageContext(
                            image_url=img,
                            link=link,
                            street=street,
                            each_price=price,
                            area=areas.split("m²")[0]
                        ).return_dict()
                    )
                except:
                    pass

        else:
            options: SearchOption = self.user.search_options
            params = await self.build_api_data()
            encoded_data = await self.params_custom_decode(params)
            request = requests.get(self.site_url + encoded_data)

            if request.status_code == 200:
                response = request.json()['result']
                clean_data = []

                for jsn in response:
                    link = ('https://cityexpert.rs/prodaja-nekretnina/'+
                        f"{CityExpertAdapter(options).get_city_value()[1]}/{jsn['propId']}/" +
                        slugify(f"{CityExpertAdapter('not').decod_room_structure(jsn['structure'])} {jsn['street']} {jsn['municipality']}"))

                    clean_data.append(
                        MessageContext(
                            image_url=self.img_url + jsn['coverPhoto'],
                            link=link,
                            street=jsn['street'],
                            price=jsn['price'],
                            floor=jsn['floor'],
                            area=jsn['size'],
                            rooms=jsn['structure'],
                            date=jsn["firstPublished"].split("T")[0],
                        ).return_dict()
                    )
        return clean_data

    async def build_link(self):
        options: SearchOption = self.user.search_options
        return (f'https://cityexpert.rs/a/novogradnja/{CityExpertAdapter(options).get_city_value()[1]}?'
                f'co={options.min_price_m2}&cd={options.max_price_m2}&pod={options.min_area}&pdo={options.max_area}&rata=All&do%5B'
                'value%5D%5Bmonth%5D=&do%5Bvalue%5D%5Byear%5D=&sort_by=field_preporucen_value')

    async def build_api_data(self):
        options: SearchOption = self.user.search_options
        return {
            "ptId": [CityExpertAdapter(options).get_home_type_value()],
            "cityId": CityExpertAdapter(options).get_city_value()[0],
            "rentOrSale": "s",
            "searchSource": "regular",
            "minPrice": options.min_price,
            "maxPrice": options.max_price,
            "minSize": options.min_area,
            "maxSize": options.max_area,
            "currentPage": f"{self.page}",
            "sort": "datedsc",
            "structure": CityExpertAdapter(options).get_room_value(),
        }

    @staticmethod
    async def params_custom_decode(params):
        encoded_data = "?req=%7B"
        for key, value in params.items():
            if isinstance(value, list):
                encoded_value = urllib.parse.quote(json.dumps(value), safe='').replace("%20", "")
            elif str(value).isalpha():
                encoded_value = urllib.parse.quote(str(value), safe='')
                encoded_value = f"%22{encoded_value}%22"
            else:
                encoded_value = urllib.parse.quote(str(value), safe='')
            encoded_data += f"%22{key}%22%3A{encoded_value}%2C"
        encoded_data = encoded_data.rstrip("%2C") + "%7D"
        return encoded_data


class CityExpertAdapter:
    def __init__(self, options):
        self.options = options

    def get_city_value(self):
        if self.options.city in [enums.Cities.EN_BELGRAD, enums.Cities.RU_BELGRAD]:
            return 1, 'beograd'
        elif self.options.city in [enums.Cities.EN_NOVI_SAD, enums.Cities.RU_NOVI_SAD]:
            return 2, 'novi-sad'
        elif self.options.city in [enums.Cities.EN_NISH, enums.Cities.RU_NISH]:
            return 3, 'nis'
        else:
            return None

    def get_home_type_value(self):
        if self.options.real_estate_type in [enums.RealEstate.EN_APARTMENT, enums.RealEstate.RU_APARTMENT]:
            return 1
        elif self.options.real_estate_type in [enums.RealEstate.EN_HOUSE, enums.RealEstate.RU_HOUSE]:
            return 2
        else:
            return None

    def get_room_value(self):

        if self.options.rooms in [enums.Rooms.APART_STUDIO]:
            return ["0.5"]
        elif self.options.rooms in [enums.Rooms.APART_1, enums.Rooms.HOUSE_1]:
            return ["1.0", "1.5", "2.0"]
        elif self.options.rooms in [enums.Rooms.APART_1_2, enums.Rooms.HOUSE_1_2]:
            return ["1.0", "1.5", "2.0", "2.5", "3.0"]
        elif self.options.rooms in [enums.Rooms.APART_3_4, enums.Rooms.HOUSE_3_4]:
            return ["3.5", "4.0", "4.5"]
        elif self.options.rooms in [enums.Rooms.APART_4_PLUS, enums.Rooms.HOUSE_4_PLUS]:
            return ["4.5", "5"]
        else:
            return ["1.0", "1.5", "2.0"]

    @staticmethod
    def decod_room_structure(structure):
        if structure == "0.5":
            return 'garsonjera stan'
        elif structure == "1.0":
            return 'jednosoban stan'
        elif structure == "1.5":
            return 'jednoiposoban stan'
        elif structure == "2.0":
            return 'dvosoban stan'
        elif structure == "2.5":
            return 'dvoiposoban stan'
        elif structure == "3.0":
            return 'trosoban stan'
        elif structure == "3.5":
            return 'troiposoban stan'
        elif structure == "4.0":
            return 'cetvorosoban stan'
        elif structure == "4.5":
            return 'cetvoroiposoban stan'
        elif structure == "5+":
            return 'petosoban i veci stan'
        return None
