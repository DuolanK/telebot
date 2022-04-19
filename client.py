from aiogram import types, Dispatcher
from create_bot import disp, bot
from keyboards import kb_client
from data_base import sqlite_db
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from data_base import sqlite_db
from typing import List, NamedTuple, Optional
import re

ID = None

# States
class FSMAdmin(StatesGroup):
     # Will be represented in storage as 'Form:name'
    adress = State()
    phone = State()
    data = State()
    zakaz = State()
    loyal_phone = State()
    loyalty = State()
    loyal = State()


amount = 1

@disp.message_handler(commands=['start'])
async def command_start(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, "Привет", reply_markup=kb_client)
    except:
        await message.reply('запустите команду в ЛС')

@disp.message_handler(commands=['режим_работы'])
async def command_worktime(message : types.Message):
    try:
        await bot.send_message(message.from_user.id, "Время доставки с 8.00 до 21.00")
    except:
        await message.reply('запустите команду в ЛС')


@disp.message_handler(commands=['Ввести свои данные'], state=None)
async def command_one(message: types.Message, state: FSMContext):
    #await sqlite_db.sql_add_ID(message.from_user.id)
    await FSMAdmin.adress.set()
    await message.reply("Привет, введи свой адрес")

@disp.message_handler(state=FSMAdmin.adress)
async def load_adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adress'] = message.text
    await FSMAdmin.next()
    await message.reply("введи номер телефона")

@disp.message_handler(state=FSMAdmin.phone)
async def load_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = int(message.text)
        data['user'] = message.from_user.id
    await sqlite_db.sql_add_command(state)
    await state.finish()
    await message.reply("Ваш адрес добавлен")

# Команда заказа
@disp.message_handler(commands=['Заказать_бутыль'], state=None)
async def command_two(message: types.Message, state: FSMContext):
    await FSMAdmin.zakaz.set()
    await message.reply("Привет, введи количество бутылей")

@disp.message_handler(content_types=['text'], state=FSMAdmin.zakaz)
async def zakazatb(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['zakaz'] = message.text
        #await Form.next()
        await bot.send_message(1184027440, data['zakaz'])
        await sqlite_db.sql_read(message)
        #dat = cur.fetchone()
        #await bot.send_message(1184027440, dat['adress'])
    except:
        await message.reply('попробуйте позже')
    await state.finish()
    await message.reply("Ваш заказ отправлен, ожидайте")

#админка is_chat_admin=True,
@disp.message_handler(commands=['admin'], state=None)
async def make_changes_command(message: types.Message, state: FSMContext):
    global ID
    ID = message.from_user.id
    await FSMAdmin.loyal_phone.set()
    await bot.send_message(message.from_user.id, 'введите номер телефона для начисления лоялти')

@disp.message_handler(state=FSMAdmin.loyal_phone)
async def loyal_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['loyal_phone'] = int(message.text)
    await FSMAdmin.next()
    await bot.send_message(message.from_user.id, 'введите размер лоялти')

@disp.message_handler(state=FSMAdmin.loyalty)
async def load_loyalty(message: types.Message, state: FSMContext):
     async with state.proxy() as data:
          data['loyalty'] = int(message.text)
     await sqlite_db.sql_loyalty(state)
     await state.finish()
     await message.reply("лоялти добавлен")

@disp.message_handler(lambda message: 'нло' in message.text)
async def ufo(message: types.Message):
    await message.answer('ноль')

@disp.message_handler(lambda message: message.text.startswith('loyal'))
async def ufo(message: types.Message):
    result = message.text[6:]
    global amount
    amount = result
    await sqlite_db.sql_loyal()

    #except:
       # await message.reply("Упс, что-то не так")


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(command_start, commands=['Старт'])
    disp.register_message_handler(command_one, commands=['Подписаться'])
    disp.register_message_handler(command_worktime, commands=['Режим_работы'])
    disp.register_message_handler(load_adress, commands=['введите_адрес'])
    disp.register_message_handler(load_phone, commands=['введи_номер'])
    disp.register_message_handler(command_two, commands=['Заказать_бутыль'])
    disp.register_message_handler(make_changes_command, commands=['admin'], state=None)
    disp.register_message_handler(loyal_phone, commands=['введите номер телефона для начисления лоялти'])
    disp.register_message_handler(load_loyalty, commands=['введите_размер_лояти'])


