from datetime import datetime
from typing import Callable, Optional, TypeVar

import iso8601


T = TypeVar("T")


def unwrap(raw: Optional[str], parser: Callable[[str], T], default: T = None) -> Optional[T]:
    if raw is not None:
        return parser(raw)
    return default


def unwrap_default(raw: Optional[str], parser: Callable[[str], T], default: T) -> T:
    if raw is not None:
        return parser(raw)
    return default


def parse_datetime(raw: str) -> datetime:
    return iso8601.parse_date(raw)
