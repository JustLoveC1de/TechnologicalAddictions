from pydantic import BaseModel

class Named(BaseModel):
    """Базовый класс для моделей, имеющих свойство name."""
    name: str
    """Название города (ru)."""

class Weather(Named):
    """Модель представления погоды в городе <name>."""
    description: str
    """Описание погоды в городе (ru)."""

class Geolocation(Named):
    """Модель представления географических координат города <name>."""
    lat: float
    """Географическая широта."""
    lon: float
    """Географическая долгота."""