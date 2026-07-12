from __future__ import annotations

from src.application.workflows.question_answering.answer_context.tables.table_header_semantics import (
    match_header_role,
    schedule_interval_labels,
)


class AnswerTableSchemaInferer:
    def infer(
        self,
        *,
        chunk_type: str | None,
        headers: list[str],
    ) -> tuple[str, dict[int, str]]:
        column_roles = {
            index: role
            for index, header in enumerate(headers)
            if (role := match_header_role(header)) is not None
        }
        schedule_columns = {
            index: interval_labels
            for index, header in enumerate(headers)
            if (interval_labels := schedule_interval_labels(header))
        }
        chunk_type_value = (chunk_type or "").strip().lower()
        roles = set(column_roles.values())

        if "task" in roles and schedule_columns:
            return "maintenance_schedule_matrix", column_roles
        if "task" in roles and "interval" in roles:
            return "maintenance_schedule_table", column_roles
        if "label" in roles and "value" in roles:
            return "key_value_table", column_roles
        if chunk_type_value in {"technical_specification", "certification_info"}:
            return "record_table", column_roles
        return "general_table", column_roles
