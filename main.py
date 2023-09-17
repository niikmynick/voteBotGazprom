import asyncio
import json
import logging
import logging.config

from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.filters import Command, Filter
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

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
performers = {}
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
async def vote_request_handler(message: Message) -> None:
    username = message.from_user.username
    logging.info(f'User {username} asked for vote menu')

    kb_builder = ReplyKeyboardBuilder()

    if db.check_vote(db.get_user_id(users[username]['fullname'])[0][0]):
        answer_text = 'Вы уже голосовали'

    else:
        users[message.from_user.username]['status'] = 'voting'

        answer_text = 'Хорошо, вот список участников:'

        for i in performers.keys():
            kb_builder.row(KeyboardButton(text=f"{performers[i]['u1']}"
                                               f"{', ' if performers[i]['u2'] else ''}"
                                               f"{performers[i]['u2']}"
                                               f" - {performers[i]['head']}"))

    await message.answer(
        answer_text,
        reply_markup=kb_builder.as_markup(resize_keyboard=True)
    )


@dp.message()
async def text_handler(message: Message) -> None:
    kb_builder = ReplyKeyboardBuilder()

    if users[message.from_user.username]['status'] == 'need_name':
        username = message.from_user.username
        fullname = message.text.strip()

        if user_access(fullname, data):
            logging.info(f'User {username} sent his name')

            if len(data[fullname]) > 1:
                answer_text = ('Ого, в компании вы не один с таким именем. '
                               'Помогите мне правильно идентифицировать вас\n'
                               'Выберите подходящий пункт из меню ниже')

                for element in data[fullname]:
                    kb_builder.row(KeyboardButton(text=f"{fullname} ({element['note']})"))

                users[message.from_user.username]['status'] = 'need_name2'

            else:
                p_id = db.get_user_id(fullname)[0][0]
                users[username]['status'] = 'logged_in'
                users[username]['person_id'] = p_id
                users[username]['fullname'] = fullname

                db.insert_tg_user(message.from_user.id, p_id, username)
                db.login_user(p_id)

                answer_text = 'Отлично, теперь ты можешь пользоваться ботом'

                kb_builder.button(text="Голосовать")

        else:
            answer_text = 'К сожалению, вам недоступно использование этого бота'
            users[username]['status'] = 'denied'

    elif users[message.from_user.username]['status'] == 'need_name2':
        username = message.from_user.username
        fullname, note = message.text[:-1].split(' (')

        if user_access(fullname, data):
            if note in [i['note'] for i in data[fullname]]:
                p_id = db.get_user_id(f"{fullname} ({note})")[0][0]

                users[username]['status'] = 'logged_in'
                users[username]['person_id'] = p_id
                users[username]['fullname'] = f"{fullname} ({note})"

                db.insert_tg_user(message.from_user.id, p_id, username)
                db.login_user(p_id)

                answer_text = 'Отлично, теперь ты можешь пользоваться ботом'

                kb_builder.button(text=f"Голосовать", callback_data=f"vote")
            else:
                answer_text = 'Вы указали неверное имя. Попробуйте еще раз'

                for element in data[fullname]:
                    kb_builder.button(text=f"{fullname} ({element['note']})")

        else:
            answer_text = 'К сожалению, вам недоступно использование этого бота'
            users[username]['status'] = 'denied'

    elif users[message.from_user.username]['status'] == 'voting':
        username = message.from_user.username

        u_id = db.get_user_id(users[username]['fullname'])[0][0]
        vote_id = 0
        for v_id in performers.keys():
            text = f"{performers[v_id]['u1']}{', ' if performers[v_id]['u2'] else ''}{performers[v_id]['u2']} - {performers[v_id]['head']}"
            if text == message.text:
                vote_id = v_id
                break

        if db.get_user_head(users[username]['fullname'])[0][0] != db.get_performers_head(vote_id)[0][0]:
            users[username]['status'] = 'logged_in'

            answer_text = 'Ваш голос записан!'

            db.register_vote(u_id, vote_id)
        else:
            answer_text = 'Вы не можете голосовать за участника из своего филиала. Выберите другого участника'

    else:
        answer_text = 'Ошибка'

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
            'status': 'logged_in',
            'fullname': i[2]
        }

    for i in db.get_performers():
        u1 = '' if not i[1] else i[1].split()
        u2 = '' if not i[2] else i[2].split()
        performers[i[0]] = {
            'u1': '' if not u1 else f'{u1[0]} {u1[1][0]}. {u1[2][0]}.',
            'u2': '' if not u2 else f'{u2[0]} {u2[1][0]}. {u2[2][0]}.',
            'head': i[3],
        }

    save_data(data)

    logging.debug('Loading data from file')

    logging.debug('Starting bot')
    await dp.start_polling(bot)


if __name__ == "__main__":
    dict_config = json.load(open('logging.conf.json', 'r'))
    logging.config.dictConfig(
        config=dict_config
    )
    asyncio.run(main())
