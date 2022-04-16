#!venv/bin/python
import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, \
    CallbackQuery
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from loguru import logger
from tortoise import Tortoise

from conf import BOT_TOKEN

from messages import MESSAGES
from models.food import Food
from models.food_category import FoodCategory
from models.user import User

from utils import States

# BOT
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

inline_btn_1 = InlineKeyboardButton('Завтрак', callback_data='1')
inline_btn_2 = InlineKeyboardButton('Обед', callback_data='2')
inline_btn_3 = InlineKeyboardButton('Ужин', callback_data='3')
inline_btn_4 = InlineKeyboardButton('Перекус', callback_data='4')
inline_btn_cancel = InlineKeyboardButton('Отмена', callback_data='Cancel')
inline_kb1 = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4,
                                                            inline_btn_cancel)

inline_btn_5 = InlineKeyboardButton('Добавить граммы и каллориии', callback_data='5')
inline_btn_6 = InlineKeyboardButton('Добавить граммы, каллориии и БЖУ', callback_data='6')

inline_kb2 = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_5, inline_btn_6, inline_btn_cancel)
cancel_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_cancel)

start_kb = ReplyKeyboardMarkup(resize_keyboard=True, )
start_kb.row('Календарь')


@dp.message_handler(state='*', commands=['start'])
async def start_command(message: types.Message, state: FSMContext):
    await User.add_user(message.from_user.id)
    message = await message.answer(MESSAGES['start'], reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.START.set()


@dp.callback_query_handler(state='*', text_contains='Cancel')
async def cancel_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await States.WAIT.set()


@dp.message_handler(state='*', commands=['change_limits'])
async def change_limit(message: types.Message, state: FSMContext):
    await User.add_user(message.from_user.id)
    message = await message.answer('Сколько каллорий в день можно употреблять? (Напиши просто цифру)',
                                   reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.START.set()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(MESSAGES['help'])


@dp.message_handler(lambda message: message.text.isdigit(),
                    state=States.START,
                    content_types=ContentType.TEXT)
async def add_colories_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.edit_message_text(
            'Калорий в день: {}'.format(message.text),
            data.get('message').chat.id,
            data.get('message').message_id
        )
        data['calories'] = message.text
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько белков в день?', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.PROT.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.PROT,
                    content_types=ContentType.TEXT)
async def add_proteins_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.edit_message_text(
            'Белков в день: {}'.format(message.text),
            data.get('message').chat.id,
            data.get('message').message_id
        )
        data['proteins'] = message.text
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько жиров в день?', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FATS.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FATS,
                    content_types=ContentType.TEXT)
async def add_fats_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.edit_message_text(
            'Жиров в день: {}'.format(message.text),
            data.get('message').chat.id,
            data.get('message').message_id
        )
        data['fats'] = message.text
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько углеводов в день?', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.CARB.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.CARB,
                    content_types=ContentType.TEXT)
async def add_carbohydrates_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await bot.edit_message_text(
            'Углеводов в день: {}'.format(message.text),
            data.get('message').chat.id,
            data.get('message').message_id
        )
        data['carbohydrates'] = message.text
        await User.add_info(message.from_user.id, data)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Сохранено')
    async with state.proxy() as data:
        data.pop('message', None)
    await States.WAIT.set()


@dp.message_handler(state='*', commands=['add_food'])
async def add_food_state(message: types.Message, state):
    user_exist = await User.is_user_not_empty(message.from_user.id)
    if user_exist:
        await message.answer('Добавляем блюдо! Какой это прием пищи?', reply_markup=inline_kb1)
        await States.FOOD_NAME.set()
    else:
        await start_command(message, state)


@dp.callback_query_handler(state=States.FOOD_NAME)
async def add_food_name_state(callback_query: types.CallbackQuery, state: FSMContext):
    message = await bot.send_message(callback_query.from_user.id,
                                     'Название блюда:', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
        data['category'] = callback_query.data
        category = await FoodCategory.get_food_cathegory(callback_query.data)
        await bot.edit_message_text(
            category.name + ':',
            callback_query.from_user.id,
            callback_query.message.message_id
        )

    await States.FOOD_WEIGHT.set()


@dp.message_handler(state=States.FOOD_WEIGHT, content_types=ContentType.TEXT)
async def add_food_weight_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await bot.edit_message_text(
            message.text,
            data.get('message').chat.id,
            data.get('message').message_id
        )
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько грамм в порции: (0, если не знаешь сколько)', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FOOD_CAL.set()


@dp.message_handler(lambda message: message.text.isdigit(),
                    state=States.FOOD_CAL, content_types=ContentType.TEXT)
async def add_food_cal_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = message.text
        await bot.edit_message_text(
            message.text + ' грамм', data.get('message').chat.id,
            data.get('message').message_id
        )
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько каллорий в порции:', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FOOD_PROT.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_PROT, content_types=ContentType.TEXT)
async def add_food_prot_state(message: types.Message, state: FSMContext):
    message_text = message.text.replace(',', '.')
    async with state.proxy() as data:
        data['calories'] = message.text
        await bot.edit_message_text(
            message_text + ' ккал', data.get('message').chat.id,
            data.get('message').message_id
        )
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько белков в порции:', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FOOD_FATS.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_FATS, content_types=ContentType.TEXT)
async def add_food_fats_state(message: types.Message, state: FSMContext):
    message_text = message.text.replace(',', '.')
    async with state.proxy() as data:
        data['proteins'] = message.text
        await bot.edit_message_text(
            message_text + ' белки', data.get('message').chat.id,
            data.get('message').message_id
        )
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько жиров в порции:', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FOOD_CARB.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_CARB, content_types=ContentType.TEXT)
async def add_food_carb_state(message: types.Message, state: FSMContext):
    message_text = message.text.replace(',', '.')
    async with state.proxy() as data:
        data['fats'] = message.text
        await bot.edit_message_text(
            message_text + ' жиры',
            data.get('message').chat.id,
            data.get('message').message_id
        )
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько углеводов в порции:', reply_markup=cancel_kb)
    async with state.proxy() as data:
        data['message'] = message
    await States.FOOD_SAVE.set()


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_SAVE, content_types=ContentType.TEXT)
async def add_food_save_state(message: types.Message, state: FSMContext):
    message_text = message.text.replace(',', '.')
    async with state.proxy() as food_data:
        food_data['carbohydrates'] = message.text

        await bot.edit_message_text(
            message_text + ' углеводы',
            food_data.get('message').chat.id,
            food_data.get('message').message_id
        )
        user = await User.filter(chat_id=message.from_user.id).get()
        await Food.add_food_for_user(
            user,
            food_data.get('category'),
            food_data.get('name'),
            food_data.get('calories'),
            food_data.get('weight'),
            food_data.get('proteins'),
            food_data.get('fats'),
            food_data.get('carbohydrates'),
        )

    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Блюдо сохранено!')
    await States.WAIT.set()


@dp.message_handler(state='*', commands=['today_food'])
async def today_food_state(message: types.Message, state: FSMContext):
    user_exist = await User.is_user_not_empty(message.from_user.id)
    if user_exist:
        food = await User.get_food_by_user(message.from_user.id)

        if food:
            user = await User.get(chat_id=message.from_user.id)
            calories = await User.get_calories_by_user(user)
            proteins = await User.get_proteins_by_user(user)
            fats = await User.get_fats_by_user(user)
            carbohydrates = await User.get_carbohydrates_by_user(user)

            message_str = ''
            for i in food:
                category = await i.category.first()
                message_str += '*{}* ({})\n_блюдо: {}\nвес: {} грамм\nкалорийность: {} ккал\nБ/Ж/У: {}/{}/{}_\n\n'.format(
                    category.name,
                    i.time.strftime("%H:%M"),
                    i.name,
                    i.weight,
                    i.calories,
                    i.proteins,
                    i.fats,
                    i.carbohydrates
                )

            message_str += 'Калорий (съедено/осталось): {:.1f}/{:.1f}\n'.format(calories, user.calories - calories)
            message_str += 'Белки: {:.1f}/{:.1f}\n'.format(proteins, user.proteins - proteins)
            message_str += 'Жиры: {:.1f}/{:.1f}\n'.format(fats, user.fats - fats)
            message_str += 'Углеводы: {:.1f}/{:.1f}\n'.format(carbohydrates, user.carbohydrates - carbohydrates)
        else:
            message_str = 'Не найдено информации'

        await message.answer(message_str, parse_mode='Markdown')
        await States.WAIT.set()
    else:
        await start_command(message, state)


@dp.message_handler(state='*', commands=['food_for_date'])
async def food_for_date_input(message: types.Message, state: FSMContext):
    user_exist = await User.is_user_not_empty(message.from_user.id)
    if user_exist:
        message = await message.answer('Выбери дату в календаре', reply_markup=start_kb)
        async with state.proxy() as food_data:
            food_data['calendar'] = message
    else:
        await start_command(message, state)


@dp.message_handler(Text(equals=['Календарь']), state='*')
async def nav_cal_handler(message: Message, state: FSMContext):
    await message.answer("Выбери дату: ", reply_markup=await SimpleCalendar().start_calendar())
    async with state.proxy() as data:
        await bot.delete_message(data.get('calendar').chat.id, data.get('calendar').message_id)


@dp.callback_query_handler(simple_cal_callback.filter(), state='*')
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackQuery(), state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'{date.strftime("%Y-%m-%d")}'
        )
        await bot.edit_message_text('Вы выбрали:', callback_query.message.chat.id, callback_query.message.message_id)
        await States.FOOD_DATE.set()
        callback_query.message.text = date.strftime("%Y-%m-%d")
        await food_for_date_state(callback_query.message, state)


@dp.callback_query_handler(simple_cal_callback.filter())
@dp.message_handler(state=States.FOOD_DATE, content_types=ContentType.TEXT)
async def food_for_date_state(message: types.Message, state: FSMContext):
    user_exist = await User.is_user_not_empty(message.chat.id)
    if user_exist:
        food = await User.get_food_by_user(message.chat.id, message.text)

        if food:
            user = await User.get(chat_id=message.chat.id)
            calories = await User.get_calories_by_user(user, message.text)
            proteins = await User.get_proteins_by_user(user, message.text)
            fats = await User.get_fats_by_user(user, message.text)
            carbohydrates = await User.get_carbohydrates_by_user(user, message.text)

            message_str = ''
            for i in food:
                category = await i.category.first()
                message_str += '*{}* ({})\n_блюдо: {}\nвес: {} грамм\nкалорийность: {} ккал\nБ/Ж/У: {}/{}/{}_\n\n'.format(
                    category.name,
                    i.time.strftime("%H:%M"),
                    i.name,
                    i.weight,
                    i.calories,
                    i.proteins,
                    i.fats,
                    i.carbohydrates
                )

            message_str += 'Калорий (съедено/осталось): {:.1f}/{:.1f}\n'.format(calories, user.calories - calories)
            message_str += 'Белки: {:.1f}/{:.1f}\n'.format(proteins, user.proteins - proteins)
            message_str += 'Жиры: {:.1f}/{:.1f}\n'.format(fats, user.fats - fats)
            message_str += 'Углеводы: {:.1f}/{:.1f}\n'.format(carbohydrates, user.carbohydrates - carbohydrates)
        else:
            message_str = 'Не найдено информации'

        await message.answer(message_str, parse_mode='Markdown')
        await States.WAIT.set()
    else:
        await start_command(message, state)


@dp.message_handler(state='*', commands=['my_limits'])
async def my_limit(message: types.Message):
    user_exist = await User.is_user_not_empty(message.from_user.id)
    if user_exist:
        user = await User.get(chat_id=message.from_user.id)
        msg = '*Лимиты*:\n'
        msg += 'калории: {}\n'.format(user.calories)
        msg += 'белки: {}\n'.format(user.proteins)
        msg += 'жиры: {}\n'.format(user.fats)
        msg += 'углеводы: {}\n'.format(user.carbohydrates)

        await message.answer(msg, parse_mode='Markdown')


@dp.message_handler(state='*', commands=['clear'])
async def clear(message: types.Message):
    user_exist = await User.is_user_not_empty(message.from_user.id)
    if user_exist:
        user = await User.get(chat_id=message.from_user.id)
        await User.delete_today(user)
        await message.answer('Таблица очищена', parse_mode='Markdown')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def database_init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['models.user', 'models.food', 'models.food_category']}
    )
    await Tortoise.generate_schemas()
    logger.info("Tortoise inited!")


def start_polling():
    loop = asyncio.get_event_loop()
    loop.create_task(database_init())
    executor.start_polling(dp, on_shutdown=shutdown, skip_updates=True)
