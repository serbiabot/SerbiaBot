from aiogram.dispatcher.filters.state import State, StatesGroup


class AreaChanger(StatesGroup):
    Change = State()


class LanguageChanger(StatesGroup):
    Change = State()


class CityChanger(StatesGroup):
    Change = State()


class RealEstateChanger(StatesGroup):
    Change = State()


class ConditionChanger(StatesGroup):
    Change = State()


class RoomChanger(StatesGroup):
    Change = State()


class FullPriceChanger(StatesGroup):
    Change = State()


class M2PriceChanger(StatesGroup):
    Change = State()


class AdminMenu(StatesGroup):
    Advertising_text = State()
    Advertising_image = State()
