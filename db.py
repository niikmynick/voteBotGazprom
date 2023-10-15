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


def get_results_sort():
    try:
        cur.execute(
            f"select person_name, person2_name, count(vote) as amount from Performers "
            f"left join Vote V on Performers.id = V.vote "
            f"group by id order by amount desc;")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)

def get_results_nosort():
    try:
        cur.execute(
            f"select person_name, person2_name, count(vote) as amount from Performers "
            f"left join Vote V on Performers.id = V.vote "
            f"group by id;")
        return cur.fetchall()

    except sqlite3.Error as e:
        logging.error(e)
