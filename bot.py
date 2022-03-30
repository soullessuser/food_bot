#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup

from db import init_db
from utils import States, add_user, add_calories, add_proteins, add_fats, add_carbohydrates, food_for_user, \
    food_cathegory_name, is_user_not_empty, food_by_user, cal_by_user, get_user_calories
from messages import MESSAGES
from conf import BOT_TOKEN

# BOT
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
init_db()
logging.basicConfig(level=logging.INFO)


inline_btn_1 = InlineKeyboardButton('Завтрак', callback_data='1')
inline_btn_2 = InlineKeyboardButton('Обед', callback_data='2')
inline_btn_3 = InlineKeyboardButton('Ужин', callback_data='3')
inline_btn_4 = InlineKeyboardButton('Перекус', callback_data='4')
inline_btn_cancel = InlineKeyboardButton('Отмена', callback_data='Cancel')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4, inline_btn_cancel)

inline_btn_5 = InlineKeyboardButton('Добавить граммы и каллориии', callback_data='5')
inline_btn_6 = InlineKeyboardButton('Добавить граммы, каллориии и БЖУ', callback_data='6')

inline_kb2 = InlineKeyboardMarkup().add(inline_btn_5, inline_btn_6, inline_btn_cancel)
cancel_kb = InlineKeyboardMarkup().add(inline_btn_cancel)


@dp.message_handler(state='*', commands=['start'])
async def start_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_user(message.from_user.id)
    await message.answer(MESSAGES['start'], reply_markup=cancel_kb)
    await state.set_state(States.all()[2])


@dp.message_handler(state='*', commands=['change_limit'])
async def change_limit(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_user(message.from_user.id)
    await message.answer('Сколько каллорий в день можно употреблять? (Напиши просто цифру)', reply_markup=cancel_kb)
    await state.set_state(States.all()[2])


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(MESSAGES['help'])


@dp.message_handler(state='*', commands=['add_food'])
async def add_food_(message: types.Message):
    if is_user_not_empty(message.from_user.id):
        state = dp.current_state(user=message.from_user.id)
        await message.answer('Добавляем блюдо! Какой это прием пищи?', reply_markup=inline_kb1)
        await state.set_state(States.all()[5])
    else:
        await start_command(message)


@dp.callback_query_handler(state='*', text_contains='Cancel')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(States.all()[0])


@dp.callback_query_handler(state=States.STATE_0)
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text=callback_query.data)


@dp.message_handler(state=States.STATE_2, content_types=ContentType.TEXT)
async def state_1(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_calories(message.from_user.id, message.text)
    await message.reply('Зафиксировал')
    # await message.answer('Сколько белков в день?')
    await state.set_state(States.all()[1])


# @dp.message_handler(state=States.STATE_2, content_types=ContentType.TEXT)
# async def state_2(message: types.Message):
#     state = dp.current_state(user=message.from_user.id)
#     add_proteins(message.from_user.id, message.text)
#     await message.reply('Зафиксировал')
#     await message.answer('Сколько жиров в день?')
#     await state.set_state(States.all()[3])
#
#
# @dp.message_handler(state=States.STATE_3, content_types=ContentType.TEXT)
# async def state_3(message: types.Message):
#     state = dp.current_state(user=message.from_user.id)
#     add_fats(message.from_user.id, message.text)
#     await message.reply('Зафиксировал')
#     await message.answer('Сколько углеводов в день?')
#     await state.set_state(States.all()[4])
#
#
# @dp.message_handler(state=States.STATE_4, content_types=ContentType.TEXT)
# async def state_4(message: types.Message):
#     state = dp.current_state(user=message.from_user.id)
#     add_carbohydrates(message.from_user.id, message.text)
#     await message.reply('Спасибо! Необходимые данные сохранены')
#     await state.set_state(States.all()[0])


@dp.callback_query_handler(state=States.STATE_5)
async def process_callback_button1(callback_query: types.CallbackQuery):
    message = await bot.send_message(callback_query.from_user.id, 'Название блюда:', reply_markup=cancel_kb)
    await bot.edit_message_text(food_cathegory_name(callback_query.data) + ':', callback_query.from_user.id,
                                callback_query.message.message_id)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.update_data(category=callback_query.data)
    await state.update_data(last_message=message)
    await state.set_state(States.all()[6])


@dp.message_handler(state=States.STATE_6, content_types=ContentType.TEXT)
async def food_name(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(name=message.text)
    data = await state.get_data()
    await bot.edit_message_text(message.text, data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько грамм в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.all()[7])


@dp.message_handler(lambda message: message.text.isdigit(),
                    state=States.STATE_7, content_types=ContentType.TEXT)
async def food_w(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(weight=message.text)
    data = await state.get_data()
    await bot.edit_message_text(message.text + ' грамм', data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько каллорий в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.all()[8])


@dp.message_handler(state=States.STATE_8, content_types=ContentType.TEXT)
async def food_c(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(calories=message.text)
    food_data = await state.get_data()
    await bot.edit_message_text(message.text + ' ккал', food_data.get('last_message').chat.id,
                                food_data.get('last_message').message_id)
    food_for_user(message.from_user.id, food_data.get('category'), food_data.get('name'), food_data.get('calories'),
                  food_data.get('weight'))

    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Блюдо сохранено!')
    await state.set_state(States.all()[0])


@dp.message_handler(state='*', commands=['today_food'])
async def today_food(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    food = food_by_user(message.from_user.id)

    cal = cal_by_user(message.from_user.id)
    user_cals = get_user_calories(message.from_user.id)
    message_str = '*Съедено каллорий:* {}\n*Осталось каллорий:* {}\n'.format(cal, user_cals - cal)

    message_str += '\n*Приемы пищи за день:*\n'
    for i in food:
        message_str += '*{}*\n{} ({}гр., {}ккал)\n\n'.format(i.category.name, i.name, i.weight, i.calories)

    await message.answer(message_str, parse_mode='Markdown')
    await state.set_state(States.all()[1])


@dp.message_handler(state='*', commands=['food_for_date'])
async def food_for_date_input(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await message.answer('Введи дату в формате: 2022-03-30', reply_markup=cancel_kb)
    await state.set_state(States.all()[3])


@dp.message_handler(state=States.STATE_3, content_types=ContentType.TEXT)
async def food_for_date(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    food = food_by_user(message.from_user.id, message.text)
    cal = cal_by_user(message.from_user.id, message.text)
    message_str = ''
    if food.exists():
        user_cals = get_user_calories(message.from_user.id)
        message_str = '*Съедено каллорий:* {}\n*Осталось каллорий:* {}\n'.format(cal, user_cals - cal)

        message_str += '\n*Приемы пищи за день:*\n'
        for i in food:
            message_str += '*{}*\n{} ({}гр., {}ккал)\n\n'.format(i.category.name, i.name, i.weight, i.calories)
    else:
        message_str = 'На выбранную дату не найдено информации'
    await message.answer(message_str, parse_mode='Markdown')
    await state.set_state(States.all()[1])


@dp.message_handler(state='*', commands=['my_limit'])
async def my_limit(message: types.Message):

    await message.answer('*Лимит*: {}'.format(get_user_calories(message.from_user.id)), parse_mode='Markdown')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def start_polling():
    executor.start_polling(dp, on_shutdown=shutdown)
