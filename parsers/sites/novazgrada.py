import re

import requests
from bs4 import BeautifulSoup

from db import enums
from db.models import SearchOption
from parsers.BaseParser import BaseParser
from parsers.sendler import MessageContext


class NovazGradaParser(BaseParser):

    def __init__(self, chat_id, page=1):
        super().__init__(chat_id, page)
        self.site_url = 'https://novazgrada.rs'

    async def send_request(self):
        link = await self.build_link()
        response = requests.get(link)

        if response.status_code == 200:
            RU = True if self.user.language == enums.Language.Ru else False
            soup = BeautifulSoup(response.text, 'html.parser')
            offers = soup.find_all('div', class_='wp-block default artbud-property-block')
            clean_data = []

            for offer in offers:
                img = offer.find('img').get('src')
                link = self.site_url + offer.find('a').get('href')
                street = offer.find('div', class_='clearfix mb-5').text.replace("\n", "")
                matches = re.findall(r'[0-9\s]+', offer.find('span', class_='artbud-price base').text)
                price = ''.join(matches).replace(' ', '').replace('\n', '')
                price = f'{price} €/m²' if price else ('договорная' if RU else 'negotiated')

                clean_data.append(
                    MessageContext(
                        image_url=img,
                        link=link,
                        street=street,
                        each_price=price,
                    ).return_dict()
                )

            return clean_data

    async def build_link(self):
        options: SearchOption = self.user.search_options
        self.options = options
        return (
            f"{self.site_url}/pretraga?"
            f"page={self.page}"
            f"{NovozgradaAdapter(options).get_rooms_values()}"
            f"&saleSqm[min]=0"
            f"&saleSqm[max]=10000"
            f"&currency=EUR"
            f"&areaCommon[min]={options.min_area}"
            f"&areaCommon[max]={options.max_area}"
        )


class NovozgradaAdapter:
    def __init__(self, options):
        self.options = options

    def get_rooms_values(self):
        if self.options.rooms in [enums.Rooms.APART_1, enums.Rooms.HOUSE_1]:
            return '&realEstate[rooms][10]=10&realEstate[rooms][15]=15&realEstate[rooms][20]=20'
        if self.options.rooms in [enums.Rooms.APART_1_2, enums.Rooms.HOUSE_1_2]:
            return '&realEstate[rooms][10]=10&realEstate[rooms][15]=15&realEstate[rooms][20]=20&realEstate[rooms][25]=25&realEstate[rooms][30]=30'
        elif self.options.rooms in [enums.Rooms.APART_2]:
            return '&realEstate[rooms][25]=25&realEstate[rooms][30]=30'
        elif self.options.rooms in [enums.Rooms.APART_3_4, enums.Rooms.HOUSE_3_4]:
            return '&realEstate[rooms][30]=30&realEstate[rooms][40]=40'
        elif self.options.rooms in [enums.Rooms.APART_4_PLUS, enums.Rooms.HOUSE_4_PLUS]:
            return '&realEstate[rooms][40]=40'
        elif self.options.rooms in [enums.Rooms.APART_STUDIO]:
            return '&realEstate[rooms][0]=0'
        return ''
