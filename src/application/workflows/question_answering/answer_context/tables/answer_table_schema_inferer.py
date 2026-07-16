from __future__ import annotations

from src.application.workflows.shared.table_kind import TableKind
from src.application.workflows.question_answering.answer_context.tables.table_type_resolution_core import (
    resolve_table_type,
)

_RESOLVED_TYPE_TO_ANSWER_KIND: dict[TableKind, str] = {
    TableKind.MAINTENANCE_SCHEDULE_MATRIX: "maintenance_schedule_matrix",
    TableKind.MAINTENANCE_SCHEDULE_TABLE: "maintenance_schedule_table",
    TableKind.KEY_VALUE_TABLE: "key_value_table",
    TableKind.SPECIFICATION_MATRIX: "specification_matrix",
    TableKind.PERFORMANCE_CURVE_MATRIX: "general_table",
    TableKind.TOC_TABLE: "general_table",
    TableKind.TROUBLESHOOTING_TABLE: "troubleshooting_table",
    TableKind.SPARE_PARTS_TABLE: "record_table",
    TableKind.CERTIFICATION_TABLE: "record_table",
    TableKind.RECORD_TABLE: "record_table",
    TableKind.GENERAL_TABLE: "general_table",
}


class AnswerTableSchemaInferer:
    def infer(
        self,
        *,
        chunk_type: str | None,
        headers: list[str],
        table_category: str | None = None,
        table_shape: str | None = None,
        rows: list[list[str]] | None = None,
    ) -> tuple[str, dict[int, str]]:
        resolved, column_roles = resolve_table_type(
            table_category=table_category,
            table_shape=table_shape,
            chunk_type=chunk_type,
            headers=headers,
            rows=rows,
        )
        return _RESOLVED_TYPE_TO_ANSWER_KIND[resolved], column_roles
