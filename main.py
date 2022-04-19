from aiogram.utils import executor
from create_bot import disp
from handlers import client
from data_base import sqlite_db


async def on_startup(_):
    print("Йоу, бот запущен")
    sqlite_db.sql_start()


client.register_handlers_client(disp)

# start long polling
if __name__ == '__main__':
    executor.start_polling(disp, skip_updates=True, on_startup=on_startup)
