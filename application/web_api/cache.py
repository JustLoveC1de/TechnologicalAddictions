from typing import Any, Callable, NamedTuple, Hashable
from collections import OrderedDict
from functools import wraps, _make_key
import asyncio

_TypedCacheInfo = NamedTuple('CacheInfo', [
    ('hits', int), 
    ('misses', int),
    ('cursize', int),
    ('maxsize', int)
])

def acache(fn: Callable, *, max_size: int = 128):
    """Декоратор, основанный на functools.lru_cache(), но для асинхронных функций.

    Возможность создания безразмерного кэша отсутствует."""

    sentinel: object = object() # украдено из исходного кода декоратора lru_cache.
    # т.к. этот объект уникален, и его нельзя встретить как значение в кэше,
    # его удобно использовать в качестве значения аргумента __default в методе get класса dict (OrderedDict)
    cache: OrderedDict = OrderedDict()
    hits: int = 0
    misses: int = 0

    @wraps(fn)
    async def fnwrap(*args, **kwargs):
        nonlocal hits, misses # такая реализация счётчиков тоже взята из исходного кода
        key: Hashable = _make_key(args, kwargs, True)
        cached: Any = cache.get(key, sentinel)
        if cached is not sentinel:
            hits += 1
            cache.move_to_end(key, True)
            return cached
        misses += 1
        res: Any = await asyncio.create_task(fn(*args, **kwargs))
        if len(cache) >= max_size:
            cache.popitem(True)
        cache[key] = res
        return res
    
    def cache_info() -> _TypedCacheInfo:
        return _TypedCacheInfo(hits, misses, len(cache), max_size)

    fnwrap.cache_info = cache_info
    return fnwrap