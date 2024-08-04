from itertools import islice
from typing import (
    Iterable,
    Iterator
)

def chunks(iterable: Iterable, size: int) -> Iterator[tuple]: # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks/22045226#22045226
    """Делит iterable на size одинаковых кортежей."""
    iterator: Iterator = iter(iterable)
    return iter(lambda: tuple(islice(iterator, size)), ())