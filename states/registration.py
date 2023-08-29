from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    City = State()
    HomeType = State()
    Condition = State()
    Room = State()
    Price = State()
    Area = State()
    Menu = State()
