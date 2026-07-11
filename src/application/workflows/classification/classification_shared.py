from __future__ import annotations

import re
from enum import Enum
from typing import TypeVar

from src.application.workflows.common.enum_label_resolver import resolve_enum_value

KEY_PATTERN = re.compile(r"[^a-z0-9]+")

_EnumT = TypeVar("_EnumT", bound=Enum)


def _normalize_label(label: str) -> str:
    return KEY_PATTERN.sub("_", label.lower()).strip("_")


def resolve_enum_label(label: str, enum_cls: type[_EnumT]) -> _EnumT:
    return resolve_enum_value(
        label,
        enum_cls,
        normalize=_normalize_label,
        match_member_name=True,
        default=enum_cls("unknown"),
    )


def build_unknown_label_errors(raw_label: str, resolved: Enum) -> list[str]:
    normalized = KEY_PATTERN.sub("_", raw_label.lower()).strip("_")
    unknown = type(resolved)("unknown")

    if resolved == unknown and normalized != unknown.value:
        return [f"Unknown label returned by model: {raw_label}"]

    return []
