from random import choice
from time import time
from aiogram import executor, types
from aiogram.types import ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, types
import fms.login, fms.create, fms.question, fms.que1, fms.que2
import db.db
from config import TOKEN_API
import yagpt.gpt
from yagpt.gpt import epi
from command import dp
from db.db import db_start, db_deader

async def on_startup(_):
    print("HI, i work")


@dp.message_handler()
async def echo_upper(message: types.Message):
    # print(message.reply_to_message['from'])
    if message.reply_to_message is not None and message.reply_to_message['from']['id'] == 7035202829:
        await message.reply(yagpt.gpt.epi(message.text))


if __name__ == '__main__':
    print('hello world')
    db_deader()

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)