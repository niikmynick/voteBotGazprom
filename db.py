import sqlite3
import logging

conn = sqlite3.connect('identifier.sqlite')
cur = conn.cursor()
connected = False


def connect():
    global conn, cur, connected
    try:
        conn = sqlite3.connect('identifier.sqlite')
        cur = conn.cursor()
        connected = True
        #
        # cur.execute("""
        # create table if not exists User (
        #     id integer primary key autoincrement,
        #     name varchar(255) not null,
        #     position varchar(255) not null,
        #     team varchar(255) not null,
        #     head varchar(255) not null,
        #     logged_in bool not null
        # );""")
        #
        # cur.execute("""
        # create table if not exists Performers (
        #     id integer primary key autoincrement,
        #     person_name varchar(255),
        #     person2_name varchar(255),
        #     head varchar(255)
        # );""")
        #
        # cur.execute("""
        # insert into Performers (person_name, person2_name, head)
        # values ('Черкасова Татьяна Григорьевна', NULL, 'АГПП'),
        #        ('Koвтун Иван Владимирович', NULL, 'МСК'),
        #        ('Шамова Евгения Владимировна', NULL, 'МСК'),
        #        ('Сутаев Мансур Магарамович', NULL, 'МСК'),
        #        ('Пахтелев Константин Вадимович', NULL, 'НН'),
        #        ('Репин Иван Ильич', NULL, 'НН'),
        #        ('Васин Денис Александрович', 'Пьянзин Данил Игоревич', 'НН'),
        #        ('Гольм Мария Александровна', NULL, 'СПб'),
        #        ('Аверьянов Алексанлр Александрович', NULL, 'СПб'),
        #        ('Сергеев Владислав Викторович', NULL, 'СПб'),
        #        ('Соколов Максим Сергеевич', NULL, 'Саратов'),
        #        ('Настин Антон Николаевич', NULL, 'Саратов'),
        #        ('Черников Алексей Олегович', 'Рассада Анна Андреевна', 'Саратов'),
        #        ('Суханова Елизавета Сергеевна', NULL, 'Саратов'),
        #        ('Саломатов Владислав Андреевич', NULL, 'Тюмень'),
        #        ('Шахматова Елизавета Константиновна', NULL, 'Тюмень'),
        #        ('Сатюкова Ксения Aлексеевна', 'Шумков Иван Игоревич', 'Тюмень');
        # """)
        #
        # cur.execute("""
        # create table if not exists Vote (
        #     person_id integer,
        #     vote integer,
        #     foreign key (person_id) references User(id),
        #     foreign key (vote) references Performers(id)
        # );""")
        #
        # cur.execute("""
        # create table if not exists TGUser (
        #     tg_id integer primary key,
        #     u_id integer,
        #     username varchar(20) not null,
        #     foreign key (u_id) references User(id)
        # );
        # """)

    except sqlite3.Error as e:
        logging.error(e)
        raise SystemExit


def get_users():
    try:
        cur.execute(f"select * from User")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def get_tg_users():
    try:
        cur.execute(f"select tg_id, username, U.name from TGUser join main.User U on U.id = TGUser.u_id")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def insert_tg_user(user_id, p_id, username):
    try:
        cur.execute(
            f"insert into TGUser (tg_id, u_id, username) values ({user_id}, {p_id}, '{username}')")
        conn.commit()

    except sqlite3.Error as e:
        logging.error(e)


def get_user_id(u_name):
    try:
        cur.execute(f"select id from User where name = '{u_name}'")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def get_user_head(u_name):
    try:
        cur.execute(f"select head from User where name = '{u_name}'")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def get_performers():
    try:
        cur.execute("select id, person_name, person2_name, head from Performers")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def get_performers_head(v_id):
    try:
        cur.execute(f"select head from Performers where id = '{v_id}'")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def insert_user(u_name, u_position, u_team, u_head):
    try:
        cur.execute(
            f"insert into User (name, position, team, head, logged_in) "
            f"values ('{u_name}', '{u_position}', '{u_team}', '{u_head}', FALSE);")
        conn.commit()

    except sqlite3.Error as e:
        logging.error(e)


def login_user(u_id):
    try:
        cur.execute(f'update User set logged_in = TRUE where id = {u_id}')
        conn.commit()

    except sqlite3.Error as e:
        logging.error(e)


def check_vote(u_id):
    try:
        cur.execute(f"select * from Vote where person_id = {u_id}")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
        return []


def register_vote(u_id, u_vote_id):
    try:
        cur.execute(
            f"insert into Vote (person_id, vote) VALUES ({u_id}, {u_vote_id});")
        conn.commit()

    except sqlite3.Error as e:
        logging.error(e)


def get_results():
    try:
        cur.execute(
            f"select person_name, person2_name, count(vote) as amount from Performers "
            f"left join Vote V on Performers.id = V.vote "
            f"group by id order by amount desc;")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
