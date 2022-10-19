from flask import g
import sqlite3

from ._tables import TABLE_DEFS

DATABASE = 'moonlight.db'


def initialize_database():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        for table_def in TABLE_DEFS:
            cur.execute(table_def)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
