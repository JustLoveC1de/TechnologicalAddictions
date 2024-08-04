from logging import (
    getLogger,
    Logger
)
from pymorphy3 import MorphAnalyzer
from pymorphy3.analyzer import Parse
from functools import lru_cache
from typing import Optional

logger: Logger = getLogger(__name__)

UNIVERSAL_PARSER: MorphAnalyzer = MorphAnalyzer()

@lru_cache
def inflect(word: str, *grammemes, title: bool = True) -> str:
    """Применяет к слову набор граммем, кэшируя результат."""
    logger.debug("Склоняем слово %s %s.", word, grammemes)
    parsed: Parse = UNIVERSAL_PARSER.parse(word)[0]
    inflected: str = parsed.inflect(set(grammemes)).word
    return inflected.title() if title else inflected