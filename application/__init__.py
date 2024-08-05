from logging import (
    getLogger,
    Logger
)
from application.data import init_app
from flask import Flask
import os.path as path
import application.log_configuration as log
import application.blueprints as bl
import tomllib

logger: Logger = getLogger(__name__)


def make_app():
    app: Flask = Flask(__name__, instance_relative_config=True)
    assert path.exists(app.instance_path), "Отсутствует папка instance с конфигурацией."

    app.config.from_mapping({
        "DATABASE_NAME": "main.db",
        "KEY": "c496993eeb9bb9a42bf39fdac739acd9",
        "CITIES": "cities.example.txt"
    })

    app.config["DATABASE_PATH"] = path.join(app.instance_path, app.config["DATABASE_NAME"])
    
    with app.app_context():
        init_app()

    log.configure_log(path.join(app.instance_path, "app.log"))

    app.register_blueprint(bl.pages)
    app.register_blueprint(bl.facts)
    return app

    