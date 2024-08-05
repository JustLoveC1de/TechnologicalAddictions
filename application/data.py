from flask import (
    g,
    current_app,
    Flask
)
from sqlite3 import (
    connect,
    Connection,
    Row
)
from typing import Optional
from requests import Session
from requests.adapters import HTTPAdapter


HEADERS: str = "Mozilla/5.0"



def get_db() -> Connection:
    db: Optional[Connection] = g.get('_database')
    if db is None:
        db = connect(current_app.config['DATABASE_PATH'])
        g._database = db
        db.row_factory = Row
    return db

def get_session() -> Session:
    session: Optional[Session] = g.get('_session')
    if session is None:
        session = Session()
        session.headers['User-Agent'] = HEADERS
        session.mount('http://', HTTPAdapter(max_retries=5))
        g._session = session
    return session

def cleanup(exception: Exception) -> None:
    db: Optional[Connection] = g.pop('_database', None)
    if db is not None:
        db.commit()
        db.close()
    session: Optional[Session] = g.pop('_session', None)
    if session is not None:
        session.close()

def init_table() -> None:
    get_db().executescript(
        """CREATE TABLE IF NOT EXISTS geolocation (
            en TEXT NOT NULL UNIQUE,
            ru TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL
        );"""
    )

def init_app() -> None:
    init_table()
    current_app.teardown_appcontext(cleanup)