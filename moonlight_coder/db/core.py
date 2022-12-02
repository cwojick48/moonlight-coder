from pathlib import Path
import sqlite3
from typing import List

from flask import g

from ._tables import TABLE_DEFS

__all__ = ['get_db', 'get_user_answers', 'check_if_user_exists', 'create_new_user', 'update_user_result',
           'get_all_usernames', 'get_user']


DATABASE = 'moonlight.db'
DATABASE_PATH = Path(__file__).parent / DATABASE


def _initialize_database(connection):
    # with sqlite3.connect(DATABASE) as con:
    cur = connection.cursor()
    for table_def in TABLE_DEFS:
        try:
            cur.execute(table_def)
        except sqlite3.OperationalError as e:
            print(f"could not initialize table: {e}")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        try:
            print('initializing database...')
            _initialize_database(db)
            print('database fully initialized')
        except Exception as e:
            print(f'problem initializing database: {e}')
    return db


def get_user_answers(connection, username: str, uuid: str = None) -> dict:
    query = f"""SELECT uuid, ignore, num_correct, num_incorrect, streak FROM answers 
    -- JOIN answers on users.username == answers.username 
    WHERE answers.username = '{username}'"""

    if uuid is not None:
        query = query + f" and uuid = '{uuid}'"

    cursor = connection.cursor()
    cursor.execute(query)
    columns = ('uuid', 'ignore', 'num_correct', 'num_incorrect', 'streak')
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return {record['uuid']: record for record in raw_results}


def update_user_result(connection, username: str, uuid: str, correct: bool):
    previous = get_user_answers(connection, username, uuid)
    if not previous:
        command = f"""INSERT INTO answers 
        VALUES ('{username}', '{uuid}', 0, {int(correct)}, {int(not correct)}, {int(correct)})"""
    else:
        if not len(previous) == 1:
            raise Exception("there should never be more than one row returned")
        previous = previous[uuid]
        command = f"""UPDATE answers
        SET num_correct = {previous['num_correct'] + int(correct)},
            num_incorrect = {previous['num_incorrect'] + int(not correct)},
            streak = {previous['streak'] + 1 if correct else 0}
        WHERE username = '{username}'
          and uuid = '{uuid}';"""

    print(f"running db command: {command}")
    cursor = connection.cursor()
    cursor.execute(command)
    connection.commit()


def get_all_usernames(connection):
    query = f"""SELECT username FROM users"""
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


USER_FIELDS = ('username', 'email', 'first_name', 'last_name')


def get_user(connection, username: str) -> List[dict]:
    query = f"""SELECT * FROM users WHERE username = '{username}'"""
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return [dict(zip(USER_FIELDS, record)) for record in result]


def check_if_user_exists(connection, username: str) -> bool:
    return len(get_user(connection, username)) == 1


def create_new_user(connection, username: str, email: str, first_name: str, last_name: str):
    if check_if_user_exists(connection, username):
        print(f"failed to insert user '{username}', user already exists")
        # this should raise an error that we handle elsewhere, although we ideally don't hit this at all
        return
    command = f"""INSERT INTO users VALUES('{username}', '{email}', '{first_name}', '{last_name}')"""
    cursor = connection.cursor()
    try:
        cursor.execute(command)
        connection.commit()
    except Exception as err:
        print(f"failed to insert user '{username}', something went wrong: {err}")


