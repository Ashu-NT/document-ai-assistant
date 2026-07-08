from __future__ import annotations

import re
from enum import Enum
from typing import TypeVar

KEY_PATTERN = re.compile(r"[^a-z0-9]+")

_EnumT = TypeVar("_EnumT", bound=Enum)


def resolve_enum_label(label: str, enum_cls: type[_EnumT]) -> _EnumT:
    normalized = KEY_PATTERN.sub("_", label.lower()).strip("_")

    for member in enum_cls:
        if normalized in {member.value, member.name.lower()}:
            return member

    return enum_cls("unknown")


def build_unknown_label_errors(raw_label: str, resolved: Enum) -> list[str]:
    normalized = KEY_PATTERN.sub("_", raw_label.lower()).strip("_")
    unknown = type(resolved)("unknown")

    if resolved == unknown and normalized != unknown.value:
        return [f"Unknown label returned by model: {raw_label}"]

    return []
