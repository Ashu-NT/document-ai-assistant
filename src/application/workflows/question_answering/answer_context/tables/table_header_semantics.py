from __future__ import annotations

import re

from src.application.workflows.shared.maintenance_text_cleaning import (
    MAINTENANCE_PLACEHOLDER_VALUES,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    SCHEDULE_INTERVAL_LABELS,
)

_HEADER_ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "label": (
        "attribute",
        "characteristic",
        "data",
        "description",
        "designation",
        "field",
        "item",
        "parameter",
        "particular",
        "particulars",
        "property",
        "specification",
    ),
    "value": ("details", "rating", "result", "setting", "value"),
    "task": (
        "activity",
        "action",
        "inspection item",
        "maintenance item",
        "maintenance task",
        "operation",
        "task",
    ),
    "interval": (
        "frequency",
        "inspection interval",
        "interval",
        "period",
        "schedule",
        "service interval",
    ),
    "component": ("assembly", "component", "equipment", "location", "part", "system"),
    "notes": (
        "comment",
        "comments",
        "note",
        "notes",
        "reference",
        "remark",
        "remarks",
        "task reference",
    ),
    "position": (
        "item",
        "item no",
        "part pos",
        "pos",
        "pos.",
        "pos nr",
        "position",
        "position no",
    ),
    "quantity": ("qty", "quantity"),
    "unit": ("unit",),
    "part_no": (
        "article no",
        "material no",
        "order no",
        "part no",
        "part number",
        "spare part no",
    ),
    "service": ("function", "service", "service function"),
    "type": ("type",),
}

_POSITIVE_SCHEDULE_MARKERS = {
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

_HEADER_PUNCTUATION_PATTERN = re.compile(r"[.:;]+")


def normalize_header(value: str) -> str:
    normalized = str(value or "").strip().lower()
    normalized = _HEADER_PUNCTUATION_PATTERN.sub(" ", normalized)
    return " ".join(normalized.split())


def match_header_role(header: str) -> str | None:
    normalized = normalize_header(header)
    for role, aliases in _HEADER_ROLE_ALIASES.items():
        if normalized == role or normalized in aliases:
            return role
    return None


def schedule_interval_label(header: str) -> str | None:
    labels = schedule_interval_labels(header)
    if not labels:
        return None
    if len(labels) == 1:
        return labels[0]
    return " / ".join(labels)


def schedule_interval_labels(header: str) -> tuple[str, ...]:
    normalized = normalize_header(header)
    if normalized in SCHEDULE_INTERVAL_LABELS:
        return (SCHEDULE_INTERVAL_LABELS[normalized],)
    if normalized.startswith("every ") or normalized.endswith(" hours"):
        return (" ".join(header.strip().split()),)

    tokens = _tokenize_schedule_header(normalized)
    if len(tokens) >= 2 and all(token in SCHEDULE_INTERVAL_LABELS for token in tokens):
        labels = [SCHEDULE_INTERVAL_LABELS[token] for token in tokens]
        return tuple(dict.fromkeys(labels))
    return ()


def is_positive_schedule_marker(value: str) -> bool:
    normalized = " ".join(str(value or "").strip().lower().split())
    if not normalized:
        return False
    if normalized in (MAINTENANCE_PLACEHOLDER_VALUES - {"x"}):
        return False
    return normalized in _POSITIVE_SCHEDULE_MARKERS


def active_schedule_labels(
    *,
    header: str,
    cell_value: str,
) -> tuple[str, ...]:
    labels = schedule_interval_labels(header)
    if not labels:
        return ()
    if len(labels) == 1:
        return labels if is_positive_schedule_marker(cell_value) else ()

    marker_tokens = _tokenize_schedule_marker(cell_value)
    if len(marker_tokens) == len(labels):
        return tuple(
            label
            for label, marker in zip(labels, marker_tokens, strict=False)
            if is_positive_schedule_marker(marker)
        )
    if is_positive_schedule_marker(cell_value):
        return labels
    return ()


def looks_identifier_label(label: str) -> bool:
    normalized = normalize_header(label)
    return any(
        token in normalized
        for token in (
            "drawing",
            "id",
            "model",
            "order code",
            "order number",
            "part no",
            "part number",
            "serial",
            "tag",
        )
    )


def _tokenize_schedule_header(value: str) -> list[str]:
    separators = value.replace("/", " ").replace(",", " ").replace(";", " ")
    return [token for token in separators.split() if token]


def _tokenize_schedule_marker(value: str) -> list[str]:
    separators = (
        str(value or "")
        .strip()
        .lower()
        .replace("/", " ")
        .replace(",", " ")
        .replace(";", " ")
    )
    return [token for token in separators.split() if token]
