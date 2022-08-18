from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import psycopg2

QIWI_PRIV_KEY = 'KEY_HERE'

bot = Bot(token='TOKEN_HERE')
ADMIN = admin_id(int)
dp = Dispatcher(bot, storage = MemoryStorage())

"""for DB"""
conn = psycopg2.connect(dbname='name_of_test_db',
                            user='db_user', password='pass', host='localhost')