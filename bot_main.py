from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime
from log_settings import LoggingSettings
from user import User


QIWI_PRIV_KEY = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InNwemt5MC0wMCIsInVzZXJfaWQiOiI3OTA0MzM3NjM4OCIsInNlY3JldCI6IjJhYmMzY2U0ZDJjNjA0NGZhMTgxMGM0MTUwY2QxNmI0N2U2YTVlNDNlNjdmMTIyNzQ5MjMwZDNiYjQ2ZDQxMTAifX0='

p2p = QiwiP2P(auth_key=QIWI_PRIV_KEY)

payment_sum = 0
payment_url = ''

bot = Bot(token='5621517130:AAFtDms1O-6PIW2hB4XotR7chuYWHSB64jQ')
ADMIN = 312472285
dp = Dispatcher(bot, storage = MemoryStorage())
kb = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(InlineKeyboardButton(text="Пополнить баланс", callback_data='request_for_sum'))
pkb = InlineKeyboardMarkup(resize_keyboard=True)
pkb.add(InlineKeyboardButton(text='Оплатить', callback_data='payment_link'))
pkb.add((InlineKeyboardButton(text="Зачислить на счет", callback_data='update_balance')))
akb = InlineKeyboardMarkup(resize_keyboard=True)
akb.add(InlineKeyboardButton(text="Список пользователей", callback_data='users'))
akb.add(InlineKeyboardButton(text="Выгрузить логи", callback_data='logs'))
akb.add(InlineKeyboardButton(text="Заблокировать пользователя", callback_data='block'))
akb.add(InlineKeyboardButton(text="Изменить баланс пользователя", callback_data='change_balance'))
user = User()
logging = LoggingSettings()


"""states for balance update"""
class UserStates(StatesGroup):
    waiting_for_payment_sum = State()
    waiting_for_payment = State()
    

"""states for admin"""
class AdminStates(StatesGroup):
    waiting_for_user_id_for_change_balance = State()
    user_id_for_change_balance_got = State()
    waiting_for_user_id_for_block = State()
    user_id_for_block_got = State()


"""commands"""

async def start(message:types.Message):
    user_exists = user.check_user_exists(message.from_user.id)
    if not user_exists:
        await user.create_user(message.from_user.id, message.from_user.first_name)
        await message.answer(f'Привет, {message.from_user.first_name}!\nЯ - бот для пополнения баланса.')
        await message.answer('Нажмите на кнопку, чтобы пополнить баланс', reply_markup=kb)
        logging.logger_info.info(f'Пользователь {user_id} подключился к боту')
    else:
        is_blocked = user.get_user_block_status(message.from_user.id)
        if not is_blocked:
            await message.answer(f'Привет, {message.from_user.first_name}!\nЯ - бот для пополнения баланса.')
            await message.answer('Нажмите на кнопку, чтобы пополнить баланс', reply_markup=kb)
            logging.logger_info.info(f'Пользователь {user_id} подключился к боту')
        else:
            await message.answer(f'Вы были заблокированы!')
            logging.logger_warn.warning(f'Заблокированный пользователь {message.from_user.id} пытался подключиться к боту!')

async def admin(message:types.Message):
    if message.from_user.id == ADMIN:
        user.set_admin_status(message.from_user.id)
        await message.answer(f'Добро пожаловать в админ панель, {message.from_user.first_name}!', reply_markup=akb)
        logging.logger_warn.warning(f'Осуществлен вход в админ-панель пользователем {message.from_user.id}')
    elif user.get_user_block_status(message.from_user.id):
        await message.answer('Вы были заблокированы')
        logging.logger_warn.warning(f'Заблокированный пользователь {message.from_user.id} пытался подключиться к боту!')
    else:
        await message.answer('Недостаточно прав')
        logging.logger_warn.warning(f'Пользователь {message.from_user.id} пытался зайти в админ-панель!')

def start_handler(dp: Dispatcher):
    dp.register_message_handler(start, commands='start', state='*')

def admin_handler(dp: Dispatcher):
    dp.register_message_handler(admin, commands='admin', state='*')

def create_bill_handler(dp: Dispatcher):
    dp.register_message_handler(create_bill, state=UserStates.waiting_for_payment_sum)

@dp.callback_query_handler(lambda c: c.data == 'request_for_sum')
async def process_callback_top_up(callback_query: types.CallbackQuery, state='*'):
    if user.get_user_block_status(callback_query.from_user.id):
        await callback_query.message.answer('Вы были заблокированы')
        logging.logger_warn.warning(f'Заблокированный пользователь {callback_query.from_user.id} пытался подключиться к боту!')
    else:
        await callback_query.message.answer(text='Введите сумму')
        await UserStates.waiting_for_payment_sum.set()
        logging.logger_info.info(f'Пользователь {callback_query.from_user.id} вводит сумму пополнения')
        await callback_query.answer()

async def create_bill(message:types.Message, state: FSMContext):
    if message.text.isdigit():
        global payment_sum
        global payment_url
        amount = int(message.text)
        await message.answer('Создаю счет для оплаты...')
        logging.logger_info.info('Создается счет')
        bill = p2p.bill(bill_id=message.from_user.id, amount=amount, lifetime=5)
        payment_sum = amount
        payment_url = p2p.check(bill_id=message.from_user.id).pay_url
        logging.logger_info.info(f'Создан счет #{bill.bill_id} на сумму {amount} для пользователя {message.from_user.id}')
        await message.answer('Счет создан!\nНажмите на кнопку, чтобы оплатить', reply_markup=pkb)
        await UserStates.next()
    else:
        await message.answer('Пожалуйста, введите число!')
        logging.logger_info.info(f'Пользователь {message.from_user.id} ввел некорректные данные')


@dp.callback_query_handler(lambda c: c.data == 'payment_link')
async def process_callback_payment_link(callback_query: types.CallbackQuery, state='*'):
    global payment_url
    if user.get_user_block_status(callback_query.from_user.id):
        await callback_query.message.answer('Вы были заблокированы')
        logging.logger_warn.warning(f'Заблокированный пользователь {callback_query.from_user.id} пытался подключиться к боту!')
    else: 
        await callback_query.url(link=payment_url)
        await UserStates.next()
        logging.logger_info.info(f'Предоставлена ссылка на счет {message.from_user.id}')

@dp.callback_query_handler(lambda c: c.data == 'top_up_account')
async def process_callback_balance_update(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if user.get_user_block_status(callback_query.from_user.id):
        await bot.send_message(callback_query.from_user.id, 'Вы были заблокированы')
        logging.logger_warn.warning(f'Заблокированный пользователь {callback_query.from_user.id} пытался подключиться к боту!')
    else:
        #if payment.check_payment_status(payment_bill_id) != 'PAID':
            #await bot.send_message(callback_query.from_user.id, 'Оплата не прошла!')
        #else:
            current_balance = user.get_user_balance(callback_query.from_user.id)
            new_balance = current_balance + payment.check_payment_amount(payment.bill_id)
            user.change_user_balance(callback_query.from_user.id, new_balance)
            await bot.send_message(callback_query.from_user.id, 'Деньги зачислены')
            



if __name__ == "__main__":
    start_handler(dp)
    admin_handler(dp)
    create_bill_handler(dp)
    executor.start_polling(dp, skip_updates=True)
    