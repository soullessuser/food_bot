#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, \
    CallbackQuery
from aiogram_calendar import simple_cal_callback, SimpleCalendar


from db import init_db
from utils import States, add_user, add_calories, add_proteins, add_fats, add_carbohydrates, food_for_user, \
    food_cathegory_name, is_user_not_empty, food_by_user, cal_by_user, \
    get_user_from_db, prot_by_user, fats_by_user, carb_by_user, clear_food_from_db
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
inline_kb1 = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4, inline_btn_cancel)

inline_btn_5 = InlineKeyboardButton('Добавить граммы и каллориии', callback_data='5')
inline_btn_6 = InlineKeyboardButton('Добавить граммы, каллориии и БЖУ', callback_data='6')

inline_kb2 = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_5, inline_btn_6, inline_btn_cancel)
cancel_kb = InlineKeyboardMarkup(resize_keyboard=True).add(inline_btn_cancel)

start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)
start_kb.row('Календарь')


@dp.message_handler(state='*', commands=['start'])
async def start_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_user(message.from_user.id)
    message = await message.answer(MESSAGES['start'], reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.START)


@dp.message_handler(state='*', commands=['change_limits'])
async def change_limit(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_user(message.from_user.id)
    message = await message.answer('Сколько каллорий в день можно употреблять? (Напиши просто цифру)', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.START)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(MESSAGES['help'])


@dp.callback_query_handler(state='*', text_contains='Cancel')
async def cancel_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(States.WAIT)


@dp.message_handler(lambda message: message.text.isdigit(), state=States.START, content_types=ContentType.TEXT)
async def add_colories_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_calories(message.from_user.id, message.text)
    data = await state.get_data()
    await bot.edit_message_text('Калорий в день: {}'.format(message.text), data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько белков в день?', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.PROT)


@dp.message_handler(lambda message: message.text.isdigit(), state=States.PROT, content_types=ContentType.TEXT)
async def add_proteins_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_proteins(message.from_user.id, message.text)
    data = await state.get_data()
    await bot.edit_message_text('Белков в день: {}'.format(message.text), data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько жиров в день?', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FATS)


@dp.message_handler(lambda message: message.text.isdigit(), state=States.FATS, content_types=ContentType.TEXT)
async def add_fats_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_fats(message.from_user.id, message.text)
    data = await state.get_data()
    await bot.edit_message_text('Жиров в день: {}'.format(message.text), data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько углеводов в день?', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.CARB)


@dp.message_handler(lambda message: message.text.isdigit(), state=States.CARB, content_types=ContentType.TEXT)
async def add_carbohydrates_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    add_carbohydrates(message.from_user.id, message.text)
    data = await state.get_data()
    await bot.edit_message_text('Углеводов в день: {}'.format(message.text), data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer('Сохранено')
    await state.set_state(States.WAIT)


@dp.message_handler(state='*', commands=['add_food'])
async def add_food_state(message: types.Message):
    if is_user_not_empty(message.from_user.id):
        state = dp.current_state(user=message.from_user.id)
        await message.answer('Добавляем блюдо! Какой это прием пищи?', reply_markup=inline_kb1)
        await state.set_state(States.FOOD_NAME)
    else:
        await start_command(message)


@dp.callback_query_handler(state=States.FOOD_NAME)
async def add_food_name_state(callback_query: types.CallbackQuery):
    message = await bot.send_message(callback_query.from_user.id, 'Название блюда:', reply_markup=cancel_kb)
    await bot.edit_message_text(food_cathegory_name(callback_query.data) + ':', callback_query.from_user.id,
                                callback_query.message.message_id)
    state = dp.current_state(user=callback_query.from_user.id)
    await state.update_data(category=callback_query.data)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_WEIGHT)


@dp.message_handler(state=States.FOOD_WEIGHT, content_types=ContentType.TEXT)
async def add_food_weight_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(name=message.text)
    data = await state.get_data()
    await bot.edit_message_text(message.text, data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько грамм в порции: (0, если не знаешь сколько)', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_CAL)


@dp.message_handler(lambda message: message.text.isdigit(),
                    state=States.FOOD_CAL, content_types=ContentType.TEXT)
async def add_food_cal_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.update_data(weight=message.text)
    data = await state.get_data()
    await bot.edit_message_text(message.text + ' грамм', data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько каллорий в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_PROT)


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_PROT, content_types=ContentType.TEXT)
async def add_food_prot_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    message_text = message.text.replace(',', '.')
    await state.update_data(calories=message_text)
    data = await state.get_data()
    await bot.edit_message_text(message_text + ' ккал', data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько белков в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_FATS)


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_FATS, content_types=ContentType.TEXT)
async def add_food_fats_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    message_text = message.text.replace(',', '.')
    await state.update_data(proteins=message_text)
    data = await state.get_data()
    await bot.edit_message_text(message_text + ' белки', data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько жиров в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_CARB)


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_CARB, content_types=ContentType.TEXT)
async def add_food_carb_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    message_text = message.text.replace(',', '.')
    await state.update_data(fats=message_text)
    data = await state.get_data()
    await bot.edit_message_text(message_text + ' жиры', data.get('last_message').chat.id,
                                data.get('last_message').message_id)
    await bot.delete_message(message.from_user.id, message.message_id)
    message = await message.answer('Сколько углеводов в порции:', reply_markup=cancel_kb)
    await state.update_data(last_message=message)
    await state.set_state(States.FOOD_SAVE)


@dp.message_handler(lambda message: message.text.replace('.', '').replace(',', '').isdigit(),
                    state=States.FOOD_SAVE, content_types=ContentType.TEXT)
async def add_food_save_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    message_text = message.text.replace(',', '.')
    await state.update_data(carbohydrates=message_text)
    food_data = await state.get_data()
    await bot.edit_message_text(message_text + ' углеводы', food_data.get('last_message').chat.id,
                                food_data.get('last_message').message_id)
    food_for_user(message.from_user.id,
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
    await state.set_state(States.WAIT)


@dp.message_handler(state='*', commands=['today_food'])
async def today_food_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    food = food_by_user(message.from_user.id)

    if food and food.exists():
        user = get_user_from_db(message.from_user.id)
        cal = cal_by_user(message.from_user.id)
        prot = prot_by_user(message.from_user.id)
        fats = fats_by_user(message.from_user.id)
        carb = carb_by_user(message.from_user.id)

        message_str = ''
        for i in food:
            message_str += '*{}* ({})\n_блюдо: {}\nвес: {} грамм\nкалорийность: {} ккал\nБ/Ж/У: {}/{}/{}_\n\n'.format(
                i.category.name,
                i.time.strftime("%H:%M"),
                i.name,
                i.weight,
                i.calories,
                i.proteins,
                i.fats,
                i.carbohydrates
            )

        message_str += 'Калорий (съедено/осталось): {:.1f}/{:.1f}\n'.format(cal, user.calories - cal)
        message_str += 'Белки: {:.1f}/{:.1f}\n'.format(prot, user.proteins - prot)
        message_str += 'Жиры: {:.1f}/{:.1f}\n'.format(fats, user.fats - fats)
        message_str += 'Углеводы: {:.1f}/{:.1f}\n'.format(carb, user.carbohydrates - carb)
    else:
        message_str = 'Не найдено информации'

    await message.answer(message_str, parse_mode='Markdown')
    await state.set_state(States.WAIT)


@dp.message_handler(state='*', commands=['food_for_date'])
async def food_for_date_input(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    message = await message.answer('Выбери дату в календаре', reply_markup=start_kb)
    await state.update_data(calendar=message)


@dp.message_handler(Text(equals=['Календарь']), state='*')
async def nav_cal_handler(message: Message):
    await message.answer("Выбери дату: ", reply_markup=await SimpleCalendar().start_calendar())
    state = dp.current_state(user=message.from_user.id)
    data = await state.get_data()
    await bot.delete_message(data.get('calendar').chat.id, data.get('calendar').message_id)


@dp.callback_query_handler(simple_cal_callback.filter(), state='*')
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackQuery()):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'{date.strftime("%Y-%m-%d")}'
        )
        state = dp.current_state(user=callback_query.message.from_user.id)
        await bot.edit_message_text('Вы выбрали:', callback_query.message.chat.id, callback_query.message.message_id)
        await state.set_state(States.FOOD_DATE)
        callback_query.message.text = date.strftime("%Y-%m-%d")
        await food_for_date_state(callback_query.message)


@dp.callback_query_handler(simple_cal_callback.filter())
@dp.message_handler(state=States.FOOD_DATE, content_types=ContentType.TEXT)
async def food_for_date_state(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    user = message.chat.id
    food = food_by_user(message.chat.id, message.text)

    if food and food.exists():
        user = get_user_from_db(user)
        cal = cal_by_user(user, message.text)
        prot = prot_by_user(user, message.text)
        fats = fats_by_user(user, message.text)
        carb = carb_by_user(user, message.text)

        message_str = ''
        for i in food:
            message_str += '*{} ({})*\n_блюдо: {}\nвес: {} грамм\nкалорийность: {} ккал\nБ/Ж/У: {}/{}/{}_\n\n'.format(
                i.category.name,
                i.time.strftime("%H:%M"),
                i.name,
                i.weight,
                i.calories,
                i.proteins,
                i.fats,
                i.carbohydrates
            )

        message_str += 'Калорий (съедено/осталось): {:.1f}/{:.1f}\n'.format(cal, user.calories - cal)
        message_str += 'Белки: {:.1f}/{:.1f}\n'.format(prot, user.proteins - prot)
        message_str += 'Жиры: {:.1f}/{:.1f}\n'.format(fats, user.fats - fats)
        message_str += 'Углеводы: {:.1f}/{:.1f}\n'.format(carb, user.carbohydrates - carb)
    else:
        message_str = 'Не найдено информации'

    await message.answer(message_str, parse_mode='Markdown', reply_markup=None)
    await state.set_state(States.WAIT)


@dp.message_handler(state='*', commands=['my_limits'])
async def my_limit(message: types.Message):
    user = get_user_from_db(message.from_user.id)
    msg = '*Лимиты*:\n'
    msg += 'калории: {}\n'.format(user.calories)
    msg += 'белки: {}\n'.format(user.proteins)
    msg += 'жиры: {}\n'.format(user.fats)
    msg += 'углеводы: {}\n'.format(user.carbohydrates)

    await message.answer(msg, parse_mode='Markdown')


@dp.message_handler(state='*', commands=['clear'])
async def clear(message: types.Message):
    await message.answer(clear_food_from_db(message.from_user.id), parse_mode='Markdown')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def start_polling():
    executor.start_polling(dp, on_shutdown=shutdown)
