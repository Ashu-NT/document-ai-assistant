from __future__ import annotations

import re

_ALNUM_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize_alnum(text: str | None) -> list[str]:
    if not text:
        return []
    return _ALNUM_PATTERN.findall(text.lower())


def normalize_alnum_text(text: str | None) -> str:
    return " ".join(tokenize_alnum(text))


def compact_alnum(text: str | None) -> str:
    return "".join(tokenize_alnum(text))
