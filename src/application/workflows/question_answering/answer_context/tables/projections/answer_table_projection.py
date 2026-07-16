from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)


@dataclass(slots=True)
class AnswerTableProjection:
    headers: list[str] = field(default_factory=list)
    body_rows: list[list[str]] = field(default_factory=list)
    has_headers: bool = False
    table_kind: TableQueryStrategy = TableQueryStrategy.GENERAL_TABLE
    column_roles: dict[int, str] = field(default_factory=dict)
