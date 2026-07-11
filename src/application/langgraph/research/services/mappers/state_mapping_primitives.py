from __future__ import annotations

from typing import Any


def str_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def enum_or_none(enum_type, value: Any):
    if not isinstance(value, str) or not value:
        return None
    try:
        return enum_type(value)
    except ValueError:
        return None
