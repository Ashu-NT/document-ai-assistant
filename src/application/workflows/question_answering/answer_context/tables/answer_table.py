from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AnswerTableRow:
    source_row_index: int
    cells: list[str]
    cells_by_header: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class AnswerTable:
    source_number: int
    chunk_id: str
    chunk_type: str | None
    document_title: str | None
    section_path: str | None
    page_start: int | None
    page_end: int | None
    headers: list[str] = field(default_factory=list)
    rows: list[AnswerTableRow] = field(default_factory=list)
    table_kind: str = "general_table"
    column_roles: dict[int, str] = field(default_factory=dict)
