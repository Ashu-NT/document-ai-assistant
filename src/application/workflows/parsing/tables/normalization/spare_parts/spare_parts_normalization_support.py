from __future__ import annotations

import re

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)

FIELD_ORDER = (
    "position",
    "quantity",
    "unit",
    "description",
    "part_no",
    "service_package",
)
FIELD_LABELS = {
    "position": "Position",
    "quantity": "Quantity",
    "unit": "Unit",
    "description": "Description",
    "part_no": "Part No.",
    "service_package": "Service package",
}
FIELD_MARKERS = {
    "position": ("position", "position no", "part pos", "pos.", "pos nr", "item no"),
    "quantity": ("qty", "quantity"),
    "unit": ("unit",),
    "description": (
        "designation",
        "denomination",
        "description",
        "size / dimension",
        "material / surface",
    ),
    "part_no": (
        "part no",
        "part number",
        "spare part no",
        "article no",
        "material no",
        "order no",
    ),
    "service_package": ("service package", "included in service package"),
}

POSITION_WITH_DOT_PATTERN = re.compile(
    r"(?P<position>[A-Za-z]?\d{1,4}\.\d{2})\s+(?P<description>.+?)(?=(?:\s+[A-Za-z]?\d{1,4}\.\d{2}\s+)|$)"
)
POSITION_TOKEN_PATTERN = re.compile(r"^[A-Za-z]?\d{1,6}(?:\.\d{2})?$")
QUANTITY_PATTERN = re.compile(r"^\d{1,4}$")
UNIT_PATTERN = re.compile(r"^[A-Za-z]{2,12}$")
PART_CODE_PATTERN = re.compile(r"^-?[A-Za-z0-9]+(?:[./-][A-Za-z0-9]+)*$")


def header_fields(cells: list[str]) -> list[str]:
    joined = " ".join(cells).casefold()
    detected: list[str] = []
    for field in FIELD_ORDER:
        if any(marker in joined for marker in FIELD_MARKERS[field]):
            detected.append(field)
    return detected


def header_output_fields(
    *,
    detected_header_fields: list[str],
    parsed_rows: list[dict[str, str]],
) -> list[str]:
    detected = list(detected_header_fields)
    for field in FIELD_ORDER:
        if field in detected:
            continue
        if any(row.get(field, "").strip() for row in parsed_rows):
            detected.append(field)
    return detected or ["description"]


def looks_position_token(value: str) -> bool:
    return bool(POSITION_TOKEN_PATTERN.match(value))


def looks_part_code(value: str) -> bool:
    if not value or not PART_CODE_PATTERN.match(value):
        return False
    return any(character.isdigit() for character in value)


def apply_tail_code(row: dict[str, str], value: str) -> None:
    normalized = normalize_cell(value)
    if not normalized:
        return
    tokens = normalized.split()
    if not tokens:
        return
    if len(tokens) >= 2 and tokens[-1].isdigit():
        row["service_package"] = tokens[-1]
        candidate = " ".join(tokens[:-1]).strip()
    else:
        candidate = normalized
    if candidate and looks_part_code(candidate):
        row["part_no"] = candidate
