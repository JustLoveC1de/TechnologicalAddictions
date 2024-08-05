from logging import (
    getLogger,
    Logger
)
from typing import (
    Any,
    Optional
)
from application.web_api.data import (
    Geolocation,
    Weather
)
from application.data import (
    get_db,
    get_session
)
from sqlite3 import (
    Cursor,
    Row
)
from requests import (
    Response,
    Session
)
from flask import current_app
import os.path as path


logger: Logger = getLogger(__name__)




def generic_request(url: str, params: dict[str, str], *, method: str = 'GET') -> list[dict[str, Any]] | dict[str, Any]:
    """Отправка запроса к сайту и получение ответа от него в виде словаря (или списка словарей)."""
    session: Session = get_session()
    response: Response = session.request(method, url, params=params, headers=session.headers)
    logger.debug(f"Успешно получили ответ от сайта {url}. {method}")
    return response.json()
    

def geocode(city: str) -> Geolocation:
    """Поиск информации о расположении города в базе данных, в случае отсутствия таковой - отправка запроса к https://openweathermap.org/ с целью
    получения географической широты и долготы."""
    cursor: Cursor = get_db().cursor()
    query: Optional[Row] = cursor.execute(
        '''
        SELECT
            ru,
            lat,
            lon
        FROM 
            geolocation
        WHERE
            en = ?;
        ''', (city, )
    ).fetchone()
    if query:
        return Geolocation(name=query['ru'], lat=query['lat'], lon=query['lon'])

    logger.debug(f"Получен запрос на получение геолокации города {city}")
    url: str = r"http://api.openweathermap.org/geo/1.0/direct"
    parameters: dict[str, str] = {"q": city, "appid": current_app.config["KEY"]}
    json: list[dict] = generic_request(url, parameters)
    try:
        geolocation: Geolocation = Geolocation(name=json[0]["local_names"]["ru"], lat=json[0]["lat"], lon=json[0]["lon"])
    except KeyError:
        logger.error(f"Полученный ответ невозможно обработать; возможно, города {city} не существует.")
        return None
    cursor.execute(
        '''
        INSERT INTO geolocation (en, ru, lat, lon)
        VALUES (?, ?, ?, ?)
        ''', (city, geolocation.name, geolocation.lat, geolocation.lon, )
    )
    return geolocation
    

    
# Первоначально хотел сделать через это перевод description в weather(), но лучше через параметр самого API.
def translation(query: str, source: str = "en", target: str = "ru") -> str:
    """Отправка запроса к https://translate.atomjump.com (одному из «зеркал» LibreTranslate) с целью получения перевода
    определённого слова."""
    url: str = r"https://translate.atomjump.com/translate"
    parameters: dict = {"q": query, "source": source, "target": target, "format": "text"}
    json: dict[str, str] = generic_request(url, parameters, method='POST')
    try:
        return json["translatedText"]
        # Результаты:
        # light intensity drizzle -> интенсивность света drizzle
        # ...
    except KeyError:
        logger.error(f"Невозможно перевести слово {query}.")
        return query
    

def weather(city: str) -> Weather:
    """Отправка запроса к https://openweathermap.org/ для получения информации на русском языке о погоде
    в городе."""
    logger.debug(f"Получен запрос на получение погоды в городе {city}.")
    url: str = r"https://api.openweathermap.org/data/2.5/weather"
    geo_info: Geolocation = geocode(city)
    parameters: dict[str, str] = {"lat": geo_info.lat, "lon": geo_info.lon, "appid": current_app.config["KEY"], "lang": "ru"}
    json: list[dict[str, str]] = generic_request(url, parameters)
    description: str = json["weather"][0]["description"]
    try:
        return Weather(name=geo_info.name, description=description)
    except KeyError:
        logger.error(f"Полученный ответ невозможно обработать; возможно, города {city} не существует.")