from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from log_settings import LoggingSettings
from user import User


bot = Bot(token='5621517130:AAFtDms1O-6PIW2hB4XotR7chuYWHSB64jQ')
ADMIN = 312472285
dp = Dispatcher(bot, storage = MemoryStorage())
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Пополнить баланс"))
akb = types.ReplyKeyboardMarkup(resize_keyboard=True)
akb.add(types.InlineKeyboardButton(text="Список пользователей"))
akb.add(types.InlineKeyboardButton(text="Выгрузить логи"))
akb.add(types.InlineKeyboardButton(text="Изменить баланс пользователя"))
akb.add(types.InlineKeyboardButton(text="Заблокировать пользователя"))
user = User()
logging = LoggingSettings()

"""states for balance update"""
class UserStates(StatesGroup):
    waiting_for_payment_sum = State()
    payment_sum_got = State()
    waiting_for_bill_creation = State()
    bill_created = State()
    waiting_for_payment = State()
    finish = State() #возможно, лучше разбить на два статуса


"""commands"""

async def start(message:types.Message):
    user_exists = user.check_user_exists(message.from_user.id)
    if not user_exists:
        await user.create_user(message.from_user.id, message.from_user.first_name)
        await message.answer(f"""Привет, {message.from_user.first_name}!\nЯ - бот для пополнения баланса.\n
                            Нажмите на кнопку, чтобы пополнить баланс""", reply_markup=kb)
    else:
        is_blocked = user.get_user_block_status(message.from_user.id)
        if not is_blocked:
            await message.answer(f"""Привет, {message.from_user.first_name}!\nЯ - бот для пополнения баланса.\n
                            Нажмите на кнопку, чтобы пополнить баланс""", reply_markup=kb)
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


if __name__ == "__main__":
    start_handler(dp)
    admin_handler(dp)
    executor.start_polling(dp, skip_updates=True)
    