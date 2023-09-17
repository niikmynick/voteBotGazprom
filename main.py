import asyncio
import json
import logging
import logging.config

from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.filters import Command, Filter
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import db
from properties import BOT_TOKEN
from utils import save_data, user_access


class TextFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text


data = {}
users = {}
admins = ['niikmynick']


bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    username = message.from_user.username

    logging.info(f'User {username} sent command /start')

    users[username] = {
        'chat_id': message.from_user.id,
        'status': 'need_name'
    }

    name = message.from_user.first_name

    answer_text = (f'Здравствуйте, {hbold(name)}!\n'
                   '\nДобро пожаловавть в бот для голосования на II Научно-практической конференции\n'
                   'Для начала работы введите свои ФИО')

    await message.answer(answer_text)


@dp.message(TextFilter('Голосовать'))
async def task_request_handler(message: Message) -> None:
    username = message.from_user.username
    logging.info(f'User {username} asked for vote menu')

    answer_text = ''
    kb_builder = ReplyKeyboardBuilder()

    await message.answer(
        answer_text,
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )


@dp.message()
async def name_handler(message: Message) -> None:
    if users[message.from_user.username]['status'] != 'need_name':
        return

    username = message.from_user.username
    fullname = message.text

    kb_builder = ReplyKeyboardBuilder()

    if user_access(fullname, data):
        logging.info(f'User {username} sent his name')

        if len(data[fullname]) > 1:
            answer_text = ''
            users[message.from_user.username]['status'] = 'need_name_2'

        else:
            users[username]['status'] = 'logged_in'

            answer_text = 'Отлично, теперь ты можешь пользоваться ботом'

            kb_builder.button(text=f"Голосовать")

    else:
        answer_text = 'К сожалению, вам недоступно использование этого бота'
        users[username]['status'] = 'denied'

    await message.answer(
        answer_text,
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )


@dp.message()
async def name2_handler(message: Message) -> None:
    if users[message.from_user.username]['status'] != 'need_name2':
        return

    username = message.from_user.username

    users[username]['status'] = 'logged_in'
    db.insert_tg_user(message.from_user.id, username)

    answer_text = 'Отлично, теперь ты можешь пользоваться ботом'
    kb_builder = ReplyKeyboardBuilder()

    kb_builder.button(text=f"Голосовать", callback_data=f"vote")

    await message.answer(
        answer_text,
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )


async def main():
    logging.debug('Connecting to database')
    db.connect()

    for i in db.get_tg_users():
        users[i[1]] = {
            'chat_id': i[0],
            'status': 'logged_in'
    }

    logging.debug('Loading data from file')

    logging.debug('Starting bot')
    await dp.start_polling(bot)


if __name__ == "__main__":
    dict_config = json.load(open('logging.conf.json', 'r'))
    logging.config.dictConfig(
        config=dict_config
    )
    asyncio.run(main())
