from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):

    WAIT = State()
    START = State()
    PROT = State()
    FATS = State()
    CARB = State()
    FOOD_NAME = State()
    FOOD_WEIGHT = State()
    FOOD_CAL = State()
    FOOD_PROT = State()
    FOOD_FATS = State()
    FOOD_CARB = State()
    FOOD_SAVE = State()
    FOOD_DATE = State()