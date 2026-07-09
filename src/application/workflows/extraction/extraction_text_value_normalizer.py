from __future__ import annotations

import re
from typing import Any

NULL_LIKE_TEXT_VALUES = {
    "",
    "null",
    "none",
    "n/a",
    "na",
    "not available",
    "not applicable",
    "-",
    "--",
}

_JSON_ARTIFACT_PATTERN = re.compile(r'^[\s\[\]\{\}:,",]+$')


def normalize_extraction_text(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, list):
        parts = [
            normalized
            for item in value
            if (normalized := normalize_extraction_text(item)) is not None
        ]
        return " ".join(parts) or None

    text = " ".join(str(value).strip().strip('"').strip("'").split())
    text = text.rstrip(" .;:")
    if not text:
        return None

    lowered = text.lower()
    if lowered in NULL_LIKE_TEXT_VALUES:
        return None

    if _looks_like_json_artifact(text):
        return None

    return text


def _looks_like_json_artifact(text: str) -> bool:
    if any(character.isalnum() for character in text):
        return False

    if _JSON_ARTIFACT_PATTERN.fullmatch(text):
        return True

    return text in {"...", "…"}
