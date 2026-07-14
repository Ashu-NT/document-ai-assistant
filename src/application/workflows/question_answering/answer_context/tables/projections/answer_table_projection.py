from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnswerTableProjection:
    headers: list[str] = field(default_factory=list)
    body_rows: list[list[str]] = field(default_factory=list)
    has_headers: bool = False
    table_kind: str = "general_table"
    column_roles: dict[int, str] = field(default_factory=dict)
