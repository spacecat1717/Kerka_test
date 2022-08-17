from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import psycopg2

QIWI_PRIV_KEY = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InNwemt5MC0wMCIsInVzZXJfaWQiOiI3OTA0MzM3NjM4OCIsInNlY3JldCI6IjJhYmMzY2U0ZDJjNjA0NGZhMTgxMGM0MTUwY2QxNmI0N2U2YTVlNDNlNjdmMTIyNzQ5MjMwZDNiYjQ2ZDQxMTAifX0='

bot = Bot(token='5621517130:AAFtDms1O-6PIW2hB4XotR7chuYWHSB64jQ')
ADMIN = 312472285
dp = Dispatcher(bot, storage = MemoryStorage())

"""for DB"""
conn = psycopg2.connect(dbname='kerka_test_db',
                            user='postgres', password='Teatea_0', host='localhost')