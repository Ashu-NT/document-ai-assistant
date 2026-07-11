from __future__ import annotations

import re

from src.application.services.answer_generation.formatting.spare_parts_row_fields import (
    has_identifying_content,
)

# Layout A (free-text variant): "<position> <qty> <unit> <description>" with
# no table markup at all, e.g. "0010 1 Pce housing".
_FREE_FORM_POSITION_PATTERN = re.compile(
    r"^(?P<pos>\d{2,6})\s+(?P<qty>\d{1,4})\s+(?P<unit>[A-Za-z]{2,10})\s+(?P<desc>.+)$"
)


def row_from_free_form_position_line(text: str) -> dict[str, str] | None:
    match = _FREE_FORM_POSITION_PATTERN.match(text)
    if match is None:
        return None
    row: dict[str, str] = {
        "position": match.group("pos"),
        "quantity": match.group("qty"),
        "unit": match.group("unit"),
    }
    description = match.group("desc").strip()
    if description:
        row["description"] = description
    if not has_identifying_content(row):
        return None
    return row
