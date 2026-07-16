from __future__ import annotations

from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)

_PROMPT_LABELS: dict[TableQueryStrategy, str] = {
    TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX: "maintenance_table",
    TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE: "maintenance_table",
    TableQueryStrategy.PERFORMANCE_CURVE_MATRIX: "performance_curve_table",
    TableQueryStrategy.SPECIFICATION_MATRIX: "specification_table",
    TableQueryStrategy.TOC_TABLE: "toc_table",
    TableQueryStrategy.TROUBLESHOOTING_TABLE: "troubleshooting_table",
    TableQueryStrategy.SPARE_PARTS_TABLE: "spare_parts_table",
    TableQueryStrategy.CERTIFICATION_TABLE: "certification_table",
    TableQueryStrategy.RECORD_TABLE: "general_table",
    TableQueryStrategy.KEY_VALUE_TABLE: "general_table",
    TableQueryStrategy.GENERAL_TABLE: "general_table",
}


def prompt_table_label_for_strategy(strategy: TableQueryStrategy) -> str:
    return _PROMPT_LABELS.get(strategy, "general_table")
