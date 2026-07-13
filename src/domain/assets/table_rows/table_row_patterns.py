from __future__ import annotations

import re
from typing import Iterable

_BOOLEAN_MARKERS = {
    "1",
    "check",
    "required",
    "x",
    "yes",
    "y",
    "●",
    "■",
    "✓",
}

_EXPLICIT_HEADER_KEYWORDS = (
    "action",
    "cause",
    "causes",
    "comments",
    "connection",
    "description",
    "details",
    "designation",
    "frequency",
    "interval",
    "item",
    "note",
    "notes",
    "parameter",
    "part no",
    "part number",
    "particulars",
    "pin",
    "position",
    "possible remedies",
    "power supply",
    "problem",
    "probable causes",
    "qty",
    "quantity",
    "rating",
    "reference",
    "refers to",
    "remarks",
    "remedies",
    "result",
    "serial number",
    "service interval",
    "signal",
    "specification",
    "symptom",
    "tag",
    "task",
    "terminal",
    "value",
    "wire",
)

_SCHEDULE_HEADERS = {
    "a",
    "annual",
    "annually",
    "before startup",
    "d",
    "daily",
    "m",
    "monthly",
    "q",
    "quarterly",
    "s",
    "semi annual",
    "semi-annual",
    "w",
    "weekly",
    "yearly",
}


def normalize_cell(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def clean_rows(rows: Iterable[Iterable[object]]) -> list[list[str]]:
    cleaned_rows: list[list[str]] = []
    for row in rows:
        cleaned_row = [normalize_cell(cell) for cell in row]
        if any(cleaned_row):
            cleaned_rows.append(cleaned_row)
    return cleaned_rows


def looks_numeric(value: str) -> bool:
    stripped = value.strip().replace(",", "").replace(".", "").replace("-", "")
    return bool(stripped) and stripped.isdigit()


def looks_boolean_marker(value: str) -> bool:
    return normalize_cell(value).casefold() in _BOOLEAN_MARKERS


def looks_interval_header(value: str) -> bool:
    normalized = normalize_cell(value).casefold()
    if not normalized:
        return False
    if normalized in _SCHEDULE_HEADERS:
        return True
    if normalized.startswith("every "):
        return True
    return "hour" in normalized or "week" in normalized or "month" in normalized or "year" in normalized


def looks_explicit_header_cell(value: str) -> bool:
    normalized = normalize_cell(value).casefold()
    if not normalized or looks_numeric(normalized):
        return False
    if looks_interval_header(normalized):
        return True
    return any(keyword in normalized for keyword in _EXPLICIT_HEADER_KEYWORDS)


def looks_label_cell(value: str) -> bool:
    normalized = normalize_cell(value)
    if not normalized:
        return False
    if looks_numeric(normalized) or looks_boolean_marker(normalized):
        return False
    if _starts_with_identifier_like_code(normalized):
        return False
    alpha_count = sum(character.isalpha() for character in normalized)
    return alpha_count >= 2


def dedupe_headers(headers: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    deduped: list[str] = []
    for header in headers:
        cleaned = normalize_cell(header)
        if not cleaned:
            deduped.append("")
            continue
        counts[cleaned] = counts.get(cleaned, 0) + 1
        if counts[cleaned] == 1:
            deduped.append(cleaned)
            continue
        deduped.append(f"{cleaned} {counts[cleaned]}")
    return deduped


def active_interval_labels(headers: list[str], row: list[str]) -> tuple[str, ...]:
    labels: list[str] = []
    for index, header in enumerate(headers):
        if index >= len(row):
            continue
        if not looks_interval_header(header):
            continue
        if not looks_boolean_marker(row[index]):
            continue
        labels.append(_normalize_interval_label(header))
    return tuple(labels)


def count_interval_columns(headers: list[str]) -> int:
    return sum(1 for header in headers if looks_interval_header(header))


def count_boolean_markers(rows: Iterable[Iterable[str]], *, column_indexes: set[int]) -> tuple[int, int]:
    positives = 0
    inspected = 0
    for row in rows:
        for index in column_indexes:
            if index >= len(row):
                continue
            value = normalize_cell(row[index])
            if not value:
                continue
            inspected += 1
            if looks_boolean_marker(value):
                positives += 1
    return positives, inspected


def _normalize_interval_label(header: str) -> str:
    normalized = normalize_cell(header).casefold()
    if normalized in {"d", "daily"}:
        return "Daily"
    if normalized in {"w", "weekly"}:
        return "Weekly"
    if normalized in {"m", "monthly"}:
        return "Monthly"
    if normalized in {"q", "quarterly"}:
        return "Quarterly"
    if normalized in {"s", "semi annual", "semi-annual"}:
        return "Semi-Annual"
    if normalized in {"a", "annual", "annually", "yearly"}:
        return "Annual"
    return normalize_cell(header)


def _starts_with_identifier_like_code(value: str) -> bool:
    return bool(re.match(r"^[A-Z0-9]{1,6}(?:[./-][A-Z0-9]{1,6})+", value.upper()))
