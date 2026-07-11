from __future__ import annotations

from typing import Iterable


def evaluate_optional_bool(enabled: bool, value: bool) -> bool | None:
    if not enabled:
        return None
    return value


def unique_preserving_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
