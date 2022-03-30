from aiogram.dispatcher.filters.state import State, StatesGroup


from db import add_user_to_db, add_calories_to_user, add_proteins_to_user, add_fats_to_user, add_carbohydrates_to_user, \
    add_food_for_user, add_food_cathegory_to_db, get_food_cathegory, user_not_empty, get_food_by_user, get_cal_by_user, \
    user_calories, get_user, get_prot_by_user, get_fats_by_user, get_carb_by_user


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

def add_user(chat_id):
    try:
        return add_user_to_db(chat_id)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def add_calories(user, calories):
    try:
        return add_calories_to_user(user, calories)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def add_proteins(user, proteins):
    try:
        return add_proteins_to_user(user, proteins)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def add_fats(user, fats):
    try:
        return add_fats_to_user(user, fats)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def add_carbohydrates(user, carbohydrates):
    try:
        return add_carbohydrates_to_user(user, carbohydrates)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def add_food(user, calories):
    try:
        return add_calories_to_user(user, calories)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def food_for_user(user, category, name, calories, weight, proteins, fats, carbohydrates):
    try:
        return add_food_for_user(
                    add_user_to_db(user),
                    add_food_cathegory_to_db(category),
                    name,
                    calories,
                    weight,
                    proteins,
                    fats,
                    carbohydrates
                )
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def food_cathegory_name(id):
    try:
        return get_food_cathegory(id).name
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def is_user_not_empty(chat):
    try:
        return user_not_empty(chat)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def get_user_calories(chat):
    try:
        return user_calories(chat)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def get_user_from_db(chat):
    try:
        return get_user(chat)
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def food_by_user(chat, date=None):
    try:
        food = get_food_by_user(chat, date)
        return food
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def cal_by_user(chat, date=None):
    try:
        cal = get_cal_by_user(chat, date)
        return cal
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def prot_by_user(chat, date=None):
    try:
        cal = get_prot_by_user(chat, date)
        return cal
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def fats_by_user(chat, date=None):
    try:
        cal = get_fats_by_user(chat, date)
        return cal
    except Exception as e:
        return 'Ошибка: {}'.format(e)


def carb_by_user(chat, date=None):
    try:
        cal = get_carb_by_user(chat, date)
        return cal
    except Exception as e:
        return 'Ошибка: {}'.format(e)