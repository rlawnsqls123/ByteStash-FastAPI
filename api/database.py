import sqlite3
from config import DB_PATH

def get_db_connection():
    conn = sqlite.connect(DB_PATH, uri=True)
    conn.row_factory = sqlite3.Row
    return conn
