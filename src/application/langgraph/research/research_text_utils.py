from __future__ import annotations

import re


def normalize_theme(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.strip().lower())
    return " ".join(normalized.split())
