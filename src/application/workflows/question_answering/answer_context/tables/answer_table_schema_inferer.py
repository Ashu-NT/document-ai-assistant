from __future__ import annotations

from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.application.workflows.question_answering.answer_context.tables.table_type_resolution_core import (
    resolve_table_type,
)

_RESOLVED_TYPE_TO_ANSWER_KIND: dict[TableQueryStrategy, str] = {
    TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX: "maintenance_schedule_matrix",
    TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE: "maintenance_schedule_table",
    TableQueryStrategy.KEY_VALUE_TABLE: "key_value_table",
    TableQueryStrategy.SPECIFICATION_MATRIX: "specification_matrix",
    TableQueryStrategy.PERFORMANCE_CURVE_MATRIX: "general_table",
    TableQueryStrategy.TOC_TABLE: "general_table",
    TableQueryStrategy.TROUBLESHOOTING_TABLE: "troubleshooting_table",
    TableQueryStrategy.SPARE_PARTS_TABLE: "record_table",
    TableQueryStrategy.CERTIFICATION_TABLE: "record_table",
    TableQueryStrategy.RECORD_TABLE: "record_table",
    TableQueryStrategy.GENERAL_TABLE: "general_table",
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
