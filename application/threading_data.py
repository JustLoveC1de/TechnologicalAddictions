from threading import (
    get_ident,
    Lock
)
from typing import Any


class ThreadingData:
    data = dict()

    def init_data() -> None:
        ThreadingData.data[get_ident()] = dict()

    def modify_data(_key: str, _value: Any) -> None:
        ThreadingData.data[get_ident()][_key] = _value
    
    def get_data(_key: str) -> Any:
        return ThreadingData.data[get_ident()].get(_key)