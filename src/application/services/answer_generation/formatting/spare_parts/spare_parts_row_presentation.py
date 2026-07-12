from __future__ import annotations

from typing import Sequence

_ROW_FIELD_LABELS: dict[str, str] = {
    "position": "Position",
    "pid_position": "P&ID Position",
    "quantity": "Quantity",
    "unit": "Unit",
    "service": "Service",
    "type": "Type",
    "description": "Description",
    "part_no": "Part No.",
    "service_package": "Service package",
    "component": "Component",
    "manufacturer": "Manufacturer",
}
_ROW_FIELD_ORDER = (
    "position",
    "pid_position",
    "quantity",
    "unit",
    "service",
    "type",
    "description",
    "part_no",
    "service_package",
    "component",
    "manufacturer",
)
_ROW_FIELD_MAX_WIDTHS: dict[str, int] = {
    "position": 14,
    "pid_position": 18,
    "quantity": 10,
    "unit": 8,
    "service": 26,
    "type": 36,
    "description": 34,
    "part_no": 18,
    "service_package": 18,
    "component": 24,
    "manufacturer": 24,
}


def visible_row_fields(rows: Sequence[dict[str, str]]) -> list[str]:
    visible_fields: list[str] = []
    for field in _ROW_FIELD_ORDER:
        if any(str(row.get(field, "")).strip() for row in rows):
            visible_fields.append(field)
    return visible_fields


def row_field_label(field: str) -> str:
    return _ROW_FIELD_LABELS[field]


def row_field_max_width(field: str) -> int:
    return _ROW_FIELD_MAX_WIDTHS[field]
