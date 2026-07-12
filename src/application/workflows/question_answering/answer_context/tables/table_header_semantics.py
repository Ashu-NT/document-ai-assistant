from __future__ import annotations

from src.application.workflows.shared.maintenance_text_cleaning import (
    MAINTENANCE_PLACEHOLDER_VALUES,
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
    "notes": ("comment", "comments", "note", "notes", "remark", "remarks"),
}

_SCHEDULE_INTERVAL_HEADERS: dict[str, str] = {
    "a": "Annual",
    "annual": "Annual",
    "annually": "Annual",
    "before startup": "Before startup",
    "d": "Daily",
    "daily": "Daily",
    "m": "Monthly",
    "monthly": "Monthly",
    "q": "Quarterly",
    "quarterly": "Quarterly",
    "s": "Semi-Annual",
    "semi annual": "Semi-Annual",
    "semi-annual": "Semi-Annual",
    "w": "Weekly",
    "weekly": "Weekly",
    "yearly": "Annual",
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


def normalize_header(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def match_header_role(header: str) -> str | None:
    normalized = normalize_header(header)
    for role, aliases in _HEADER_ROLE_ALIASES.items():
        if normalized == role or normalized in aliases:
            return role
    return None


def schedule_interval_label(header: str) -> str | None:
    normalized = normalize_header(header)
    if normalized in _SCHEDULE_INTERVAL_HEADERS:
        return _SCHEDULE_INTERVAL_HEADERS[normalized]
    if normalized.startswith("every ") or normalized.endswith(" hours"):
        return " ".join(header.strip().split())
    return None


def is_positive_schedule_marker(value: str) -> bool:
    normalized = " ".join(str(value or "").strip().lower().split())
    if not normalized:
        return False
    if normalized in (MAINTENANCE_PLACEHOLDER_VALUES - {"x"}):
        return False
    return normalized in _POSITIVE_SCHEDULE_MARKERS


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
