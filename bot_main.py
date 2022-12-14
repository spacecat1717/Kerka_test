from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime
from log_settings import LoggingSettings
from user import User
import main_settings

"""API settings"""
p2p = QiwiP2P(auth_key=main_settings.QIWI_PRIV_KEY)

"""basic settings"""
bot = main_settings.bot
ADMIN = main_settings.ADMIN
dp = main_settings.dp
user = User()
logging = LoggingSettings()

"""main keyboard"""
kb = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(InlineKeyboardButton(text="Пополнить баланс", callback_data='request_for_sum'))

"""admin keyboard"""
akb = InlineKeyboardMarkup(resize_keyboard=True)
akb.add(InlineKeyboardButton(text="Список пользователей", callback_data='users'))
akb.add(InlineKeyboardButton(text="Выгрузить логи", callback_data='logs'))
akb.add(InlineKeyboardButton(text="Заблокировать пользователя", callback_data='block'))
akb.add(InlineKeyboardButton(text="Изменить баланс пользователя", callback_data='change_balance'))


"""states for balance update"""
class UserStates(StatesGroup):
    waiting_for_payment_sum = State()
    waiting_for_payment = State()
    

"""states for admin"""
class AdminStates(StatesGroup):
    waiting_for_user_id_for_change_balance = State()
    waiting_for_user_id_for_block = State()

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

def admin_block_handler(dp: Dispatcher):
    dp.register_message_handler(block_user, state=AdminStates.waiting_for_user_id_for_block)

def admin_change_balance_handler(dp: Dispatcher):
    dp.register_message_handler(change_balance, state=AdminStates.waiting_for_user_id_for_change_balance)

def create_bill_handler(dp: Dispatcher):
    dp.register_message_handler(create_bill, state=UserStates.waiting_for_payment_sum)

@dp.callback_query_handler(lambda c: c.data == 'users')
async def process_callback_users(callback_query: types.CallbackQuery):
    if not user.get_user_admin_status(callback_query.from_user.id):
        await callback_query.message.answer('Недостаточно прав!')
        logging.logger_warn.warning(f'Пользователь {callback_query.from_user.id} пытался зайти в админ-панель!')
    else:
        users_list = user.get_all_users()
        for u in users_list:
            await callback_query.message.answer(f"ID:{u['user_id']}\nИмя:{u['username']}\nБаланс:{u['balance']}")
        logging.logger_info.info('Выгружен список пользователей')

@dp.callback_query_handler(lambda c: c.data == 'logs') 
async def process_callback_logs(callback_query: types.CallbackQuery):
    if not user.get_user_admin_status(callback_query.from_user.id):
        await callback_query.message.answer('Недостаточно прав!')
        logging.logger_warn.warning(f'Пользователь {callback_query.from_user.id} пытался зайти в админ-панель!')
    else: 
        await callback_query.message.reply_document(open('info.log','rb'))
        await callback_query.message.reply_document(open('critical.log', 'rb'))
        logging.logger_info.info('Выгружены логи')

@dp.callback_query_handler(lambda c: c.data == 'block')
async def process_callback_block(callback_query: types.CallbackQuery):
    if not user.get_user_admin_status(callback_query.from_user.id):
        await callback_query.message.answer('Недостаточно прав!')
        logging.logger_warn.warning(f'Пользователь {callback_query.from_user.id} пытался зайти в админ-панель!')
    else:
        await callback_query.message.answer(text='Введите ID пользователя')
        logging.logger_info.info('Запрошен ID пользователя для блокировки')
        await AdminStates.waiting_for_user_id_for_block.set()

@dp.callback_query_handler(lambda c: c.data == 'change_balance')
async def process_callback_change_balance(callback_query: types.CallbackQuery):
    if not user.get_user_admin_status(callback_query.from_user.id):
        await callback_query.message.answer('Недостаточно прав!')
        logging.logger_warn.warning(f'Пользователь {callback_query.from_user.id} пытался зайти в админ-панель!')
    else:
        await callback_query.message.answer(text='Введите ID пользователя и сумму через пробел')
        logging.logger_info.info('Запрошены данные пользователя для изменения баланса')
        await AdminStates.waiting_for_user_id_for_change_balance.set()

async def block_user(message:types.Message, state: FSMContext):
    if message.text.isdigit():
        if not user.check_user_exists(int(message.text)):
          await message.answer('Такого пользователя не существует! Проверьте данные') 
          logging.logger_error.error(f'Введены некорректные данные для блокировки: ID {message.text} ')
        else:
            if user.get_user_block_status(int(message.text)):
                await message.answer('Пользователь уже заблокирован!') 
            else:
                user.set_block(int(message.text))
                await message.answer(f'Пользователь {message.text} теперь заблокирован!') 
    else:
        await message.answer('Пожалуйста, введите число!')
        logging.logger_error.error('Введены некорректные данные для блокировки: не число')
    await state.finish()                

async def change_balance(message:types.Message, state: FSMContext):
    data = message.text.split(' ')
    user_id = int(data[0])
    amount = int(data[1])
    if not user.check_user_exists(user_id):
          await message.answer('Такого пользователя не существует! Проверьте данные') 
          logging.logger_error.error(f'Введены некорректные данные для блокировки: ID {message.text} ')
    else:
        if user.change_user_balance(user_id, amount):
            await message.answer(f'Готово! Теперь на счету {user_id} {amount} рублей')
            logging.logger_info.info(f'Баланс {user_id} изменен на {amount} рублей')
        else:
            await message.answer('Не удалось изменить баланс(')
            logging.logger_crit.critical('ИЗМЕНЕНИЕ БАЛАНСА НЕ ВЫПОЛНЕНО!!!')
    await state.finish()

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
        amount = int(message.text)
        await message.answer('Создаю счет для оплаты...')
        logging.logger_info.info('Создается счет')
        bill = p2p.bill(bill_id=message.from_user.id+1, amount=amount, lifetime=5)
        payment_url = p2p.check(bill_id=message.from_user.id+1).pay_url
        pkb_btn_1 = InlineKeyboardButton('Оплатить', url=payment_url)
        pkb_btn_2 = (InlineKeyboardButton(text="Зачислить на счет", callback_data='update'))
        pkb_mark_1 = InlineKeyboardMarkup.add(pkb_btn_1)
        pkb_full = InlineKeyboardMarkup(row_width=2).add(pkb_btn_1)
        pkb_full.add(pkb_btn_2)
        logging.logger_info.info(f'Создан счет #{bill.bill_id} на сумму {amount} для пользователя {message.from_user.id}')
        await message.answer('Счет создан!\nНажмите на кнопку, чтобы оплатить', reply_markup=pkb_full)
        await state.finish()
    else:
        await message.answer('Пожалуйста, введите число!')
        logging.logger_info.info(f'Пользователь {message.from_user.id} ввел некорректные данные')

@dp.callback_query_handler(lambda c: c.data == 'update')
async def process_callback_balance_update(callback_query: types.CallbackQuery):
    if user.get_user_block_status(callback_query.from_user.id):
        await callback_query.message.answer('Вы были заблокированы')
        logging.logger_warn.warning(f'Заблокированный пользователь {callback_query.from_user.id} пытался подключиться к боту!')
    else:
        if p2p.check(bill_id=callback_query.from_user.id+1).status != 'PAID':
            await callback_query.message.answer(text='Оплата не прошла!')
            logging.logger_warn.warning(f'Пользователь {callback_query.from_user.id} пытался пополнить баланс с неоплаченным счетом!')
        else:
            current_balance = user.get_user_balance(callback_query.from_user.id)
            new_balance = current_balance + float(p2p.check(bill_id=callback_query.from_user.id+1).amount)
            logging.logger_info.info(f'Производится зачисление средств на баланс пользователя {callback_query.from_user.id}')
            user.change_user_balance(callback_query.from_user.id, new_balance)
            await callback_query.message.answer(text='Деньги зачислены')
            logging.logger_info.info(f'Деньги зачислены. Баланс пользователя {new_balance}')
               

if __name__ == "__main__":
    start_handler(dp)
    admin_handler(dp)
    create_bill_handler(dp)
    admin_block_handler(dp)
    admin_change_balance_handler(dp)
    executor.start_polling(dp, skip_updates=True)
    