from logging import (
    getLogger,
    Logger
)
from sqlite3 import (
    connect,
    Connection,
    Cursor
)
from application.threading_data import (
    ThreadingData
)
from requests import Session
from requests.adapters import HTTPAdapter
from flask import Flask
import os.path as path
import application.log_configuration as log
import application.blueprints as bl
import tomllib
import atexit

logger: Logger = getLogger(__name__)
data: ThreadingData = ThreadingData

def cleanup(database: Connection, session: Session):
    logger.debug("Закрываем сессию и отключаемся от базы данных.")
    session.close()
    database.commit()
    database.close()


def make_app():
    data.init_data()
    app: Flask = Flask(__name__, instance_relative_config=True)
    assert path.exists(app.instance_path), "Отсутствует папка instance с конфигурацией."

    app.config.from_file("config.toml", load=tomllib.load, text=False)

    session: Session = Session()
    adapter: HTTPAdapter = HTTPAdapter(max_retries=3)
    session.mount("http://", adapter)
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0" # По неизвестной причине, API прерывает подключения с стандартным User Agent библиотеки requests.
    data.modify_data("session", session)

    database: Connection = connect(path.join(app.instance_path, app.config["DATABASE_NAME"]))
    cursor: Cursor = database.cursor()
    
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS geolocation (
            en TEXT NOT NULL UNIQUE,
            ru TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL
        );
        '''
    ) # rowid (первичный ключ) будет создан неявно, поэтому смысла в явном его указании нет

    data.modify_data("database", database)
    data.modify_data("cursor", cursor)

    atexit.register(cleanup, database, session)

    log.configure_log(path.join(app.instance_path, "app.log"))

    app.register_blueprint(bl.pages)
    app.register_blueprint(bl.facts)
    return app

    