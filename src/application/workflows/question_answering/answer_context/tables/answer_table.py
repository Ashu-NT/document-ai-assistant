from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)


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
    table_kind: TableQueryStrategy = TableQueryStrategy.GENERAL_TABLE
    column_roles: dict[int, str] = field(default_factory=dict)
    logical_table_family_id: str | None = None
    physical_table_ids: list[str] = field(default_factory=list)
    table_category: str | None = None
    table_category_confidence: float | None = None
    table_shape: str | None = None
    table_structure_quality: float | None = None
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)
    row_start: int | None = None
    row_end: int | None = None
