import sqlite3
from tables import TABLE_DEFS

DATABASE_NAME = 'moonlight.db'


def initialize_database():
    with sqlite3.connect(DATABASE_NAME) as con:
        cur = con.cursor()
        for table_def in TABLE_DEFS:
            cur.execute(table_def)


