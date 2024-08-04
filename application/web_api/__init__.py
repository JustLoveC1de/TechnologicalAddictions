from logging import (
    getLogger,
    Logger
)
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Iterator
from time import perf_counter
from random import sample
from flask import current_app
from application.web_api.data import Weather
from application.web_api.weather import weather
from application.web_api.lang import inflect
import application.util as util
import os.path as path

logger: Logger = getLogger(__name__)



CITIES: list[str] = []


def init_cities() -> None:
    logger.info("Заполняем список городов.")
    with open(path.join(current_app.instance_path, current_app.config["CITIES"]), "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            CITIES.append(line)
    if not len(CITIES):
        logger.critical("Файл с городами пуст!")


def get_cities(count: int) -> list[str]:
    if not len(CITIES):
        init_cities()
    return sample(CITIES, k=count)


def weather_facts(count: int) -> set[str]:
    start: float = perf_counter()
    strings: set[str] = set()
    cities: list[str] = get_cities(count*2)
    local_weather: tuple[Weather] = (weather(city) for city in cities)
    for pair in util.chunks(local_weather, 2):
        weather1, weather2 = (info.description for info in pair)
        city1, city2 = (inflect(info.name, "loct").title()
                        for info in pair)
        strings.add(f"В {city1} - {weather1}, а в {city2} - {weather2}.")
    logger.debug(f"Длительность выполнения: {perf_counter() - start}")
    return strings