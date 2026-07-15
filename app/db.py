import sqlite3
from contextlib import contextmanager
from .config import DB_PATH

def connect(path=None):
    target = path or DB_PATH
    if str(target) != ':memory:':
        from pathlib import Path
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), isolation_level=None, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=15000')
    initialize(conn)
    return conn

def initialize(conn):
    conn.executescript('\n    CREATE TABLE IF NOT EXISTS records (\n      resource TEXT NOT NULL, id TEXT NOT NULL, payload TEXT NOT NULL,\n      version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL,\n      updated_at TEXT NOT NULL, PRIMARY KEY(resource,id)\n    );\n    CREATE TABLE IF NOT EXISTS audit (\n      sequence INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL,\n      resource TEXT NOT NULL, record_id TEXT NOT NULL, occurred_at TEXT NOT NULL\n    );\n    CREATE INDEX IF NOT EXISTS records_resource ON records(resource);\n    CREATE TABLE IF NOT EXISTS checkout_requests (key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL);\n    ')

@contextmanager
def transaction(conn):
    if conn.in_transaction:
        yield conn
        return
    conn.execute('BEGIN IMMEDIATE')
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
