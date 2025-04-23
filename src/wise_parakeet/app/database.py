import sqlite3
from flask import current_app, g

def get_db_conn() -> sqlite3.Connection:
    '''
    Establishes a SQLite database connection
    and stores it in the current global app context
    '''

    if 'db_conn' not in g:
        db_conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        db_conn.row_factory = sqlite3.Row
        g.db_conn = db_conn

    return g.db_conn

def close_db_conn(exception:Exception|None=None):
    '''
    Terminates an active SQLite database connection if one was opened
    '''

    db_conn = g.pop('db_conn', None)

    if db_conn is not None:
        db_conn.close()

def init_db(schema:str|None=None):
    '''
    Initializes a SQLite database according to the provided schema 
    and defines how to close an active connection 
    when the current app context is finished
    '''

    db_conn = get_db_conn() # connect to database

    if schema is not None:
        db_conn.executescript(schema)

    current_app.teardown_appcontext(close_db_conn)
