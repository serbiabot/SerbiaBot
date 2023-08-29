from enum import Enum


class Language(str, Enum):
    Ru = 'Русский 🇷🇺'
    En = 'English 🇬🇧'


class Cities(str, Enum):
    RU_BELGRAD = 'Белград'
    RU_NOVI_SAD = 'Нови-Сад'
    RU_VALEVO = 'Валево' 
    RU_VRNACHKA = 'Врнячка Баня'
    RU_ZRENYANIN = 'Зренянин'
    RU_LOZNICA = 'Лозница' 
    RU_KRALEVO = 'Кралево' 
    RU_KRAGUEVAC = 'Крагуевац' 
    RU_NISH = 'Ниш'
    RU_PANCHEVO = 'Панчево' 
    RU_PIROT = 'Пирот' 
    RU_SOMBOR = 'Сомбор'
    RU_SUBOTICA = 'Суботица'
    RU_UZHICE = 'Ужице'
    RU_CHACHAK = 'Чачак'
    RU_SHABAC = 'Шабац'
    RU_JAGODINA = 'Ягодина'
    EN_BELGRAD = 'Belgrade'
    EN_NOVI_SAD = 'Novi-Sad'
    EN_VALEVO = 'Valevo'
    EN_VRNACHKA = 'Vrnyachka Banya'
    EN_ZRENYANIN = 'Zrenyanin'
    EN_YAGODINA = 'Yagodina'
    EN_KRALEVO = 'Kralevo'
    EN_KRAGUEVAC = 'Kraguevac'
    EN_NISH = 'Nish'
    EN_PANCHEVO = 'Panchevo'
    EN_PIROT = 'Pirot'
    EN_SOMBOR = 'Sombor'
    EN_SUBOTICA = 'Subotica'
    EN_UZHICE = 'Uzhice'
    EN_CHACHAK = 'Chachak'
    EN_LOZNICA = 'Loznica'
    EN_SHABAC = 'Shabac'
    EN_JAGODINA = 'Jagodina'


class Rooms(str, Enum):
    APART_STUDIO = '0.5'
    APART_1 = '1'
    APART_2 = '2'
    APART_1_2 = '1-2'
    APART_3_4 = '3-4'
    APART_4_PLUS = '4+'
    HOUSE_1 = '0.5 - 1'
    HOUSE_1_2 = '1 - 2'
    HOUSE_3_4 = '3 - 4'
    HOUSE_4_PLUS = '4 +'


class RealEstate(str, Enum):
    EN_HOUSE = 'House'
    EN_APARTMENT = 'Apartment'
    RU_HOUSE = 'Дом'
    RU_APARTMENT = 'Квартира'


class PropertyCondition(str, Enum):
    EN_NEW = 'New'
    EN_OLD = 'Secondary'
    EN_ALL = 'Any'
    RU_NEW = 'Новое'
    RU_OLD = 'Вторичное'
    RU_ALL = 'Любое'


class Menu(str, Enum):
    EN_SEARCH = 'Lets search 🔎'
    EN_OPTIONS = 'Options ⚙️'
    RU_SEARCH = 'Начать поиск 🔎'
    RU_OPTIONS = 'Опции ⚙️'


class MenuContinue(str, Enum):
    EN_SEARCH = 'Continue 🔎'
    EN_OPTIONS = 'Options ⚙️'
    RU_SEARCH = 'Продолжить 🔎'
    RU_OPTIONS = 'Опции ⚙️'


class OptionsMenu(str, Enum):
    EN_LANGUAGE = 'Language'
    EN_CITY = 'City'
    EN_HOME_TYPE = 'Real estate type'
    EN_ROOMS = 'Rooms'
    EN_PRICE = 'Price'
    EN_AREA = 'Area'
    EN_CONDITION = 'Property condition'
    EN_STOP_BOT = 'Notifications \non \ off ✅'
    RU_LANGUAGE = 'Язык'
    RU_CITY = 'Город'
    RU_HOME_TYPE = 'Вид недвижимости'
    RU_ROOMS = 'Комнаты'
    RU_PRICE = 'Цена'
    RU_AREA = 'Площадь'
    RU_CONDITION = 'Состояние жилья'
    RU_STOP_BOT = 'Уведомления \nвкл \ выкл ✅'


class PriceType(str, Enum):
    EN_FULL_PRICE = 'Full price'
    EN_M2_PRICE = 'Price/m2'
    RU_FULL_PRICE = 'Полная цена'
    RU_M2_PRICE = 'Цена/м2'


class Notifications(str, Enum):
    EN_EMPTY_PARSE = ('At the moment there are no results for your parameters, we will notify you '
                      'when they appear (or you can expand the search parameters)')
    RU_EMPTY_PARSE = ('На данный момент по вашим параметрам нет результатов, мы уведомим, когда'
                      ' появятся (или можете расширить параметры поиска)')


class AdminPanel(str, Enum):
    RU_SET_ADVERTISING = 'Настроить рекламное сообщение'
    # EN_ADVERTISING = 'Set up promotional message'
    RU_SEE_ADVERTISING = 'Посмотреть рекламное сообщение'
    # EN_SEE_ADVERTISING = 'See promotional message'


class Advertising_options(str, Enum):
    RU_TEXT = 'Настроить текст рекламы (обязательно)'
    RU_IMAGE = 'Загрузить изображение рекламы (необязательно)'


class ReminderNote(str, Enum):
    RU_NOTE = """
📋 СПРАВКА ПО БОТУ:
В Сербии структура квартир имеет более подробную градацию, можете ознакомиться 💁‍♀️
📌 Какие структуры есть: 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.5 | 4.0 | 4+

🛏 Одна спальня:
0.5 : студия (до 26 м2)
1.0 : одна многофункциональная комната и кухня
1.5 : спальня для одного человека (от 7 кв.м) и гостиная с кухней 
2.0 : одна спальня для двоих (от 9 кв.м) и гостиная с кухней.

🛏 Две спальни:
2.5 : две спальни и гостиная совмещена с кухней
3.0 : две спальни и гостиная зонирована от кухни

🛏 Три спальни:
3.5 : три спальни и гостиная совмещена с кухней
4.0 : три спальни, кухня зонирована от гостиной
"""
    EN_NOTE = """
📋 BOT HELP:
In Serbia, the structure of apartments has a more detailed gradation, you can find 💁‍♀️
📌 What structures are there: 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.5 | 4.0 | 4+

🛏 One bedroom:
0.5 : studio (up to 26 m2)
1.0 : one multifunctional room and kitchen
1.5: a bedroom for one person (from 7 sq.m.) and a living room with a kitchen
2.0 : one bedroom for two (from 9 sq.m.) and a living room with a kitchen.

🛏 Two bedrooms:
2.5 : two bedrooms and a living room combined with a kitchen
3.0 : two bedrooms and a living room zoned from the kitchen

🛏 Three bedrooms:
3.5 : three bedrooms and a living room combined with a kitchen
4.0 : three bedrooms, the kitchen is zoned from the living room
"""
