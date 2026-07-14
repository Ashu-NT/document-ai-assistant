from __future__ import annotations

from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    looks_like_maintenance_task,
)
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
        table_category: str | None = None,
        rows: list[list[str]] | None = None,
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
        table_category_value = (table_category or "").strip().lower()
        roles = set(column_roles.values())

        if schedule_columns:
            implicit_roles = self._infer_implicit_maintenance_roles(
                headers=headers,
                rows=rows or [],
                schedule_columns=schedule_columns,
                existing_roles=column_roles,
            )
            if implicit_roles:
                column_roles.update(implicit_roles)
                roles = set(column_roles.values())

        if "task" in roles and schedule_columns:
            return "maintenance_schedule_matrix", column_roles
        if "task" in roles and "interval" in roles:
            return "maintenance_schedule_table", column_roles
        if "label" in roles and "value" in roles:
            return "key_value_table", column_roles
        if table_category_value == "troubleshooting_table":
            return "troubleshooting_table", column_roles
        if table_category_value in {
            "technical_data_table",
            "operating_limits_table",
            "certification_table",
            "connection_table",
            "identifier_table",
            "operation_reference_table",
            "sensor_instrument_table",
            "spare_parts_table",
        }:
            return "record_table", column_roles
        if chunk_type_value in {"technical_specification", "certification_info"}:
            return "record_table", column_roles
        return "general_table", column_roles

    def _infer_implicit_maintenance_roles(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
        schedule_columns: dict[int, tuple[str, ...]],
        existing_roles: dict[int, str],
    ) -> dict[int, str]:
        if not rows:
            return {}

        implicit_roles: dict[int, str] = {}
        notes_index = self._implicit_notes_index(headers, existing_roles)
        if notes_index is not None:
            implicit_roles[notes_index] = "notes"

        task_index = self._implicit_task_index(
            headers=headers,
            rows=rows,
            schedule_columns=schedule_columns,
            existing_roles={**existing_roles, **implicit_roles},
        )
        if task_index is None:
            return implicit_roles

        implicit_roles[task_index] = "task"
        return implicit_roles

    @staticmethod
    def _implicit_notes_index(
        headers: list[str],
        existing_roles: dict[int, str],
    ) -> int | None:
        for index, role in existing_roles.items():
            if role == "notes":
                return index
        for index, header in enumerate(headers):
            normalized = " ".join(str(header or "").strip().lower().split())
            if normalized in {"reference", "task reference"}:
                return index
        return None

    def _implicit_task_index(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
        schedule_columns: dict[int, tuple[str, ...]],
        existing_roles: dict[int, str],
    ) -> int | None:
        best_index: int | None = None
        best_score = 0

        for index, header in enumerate(headers):
            if existing_roles.get(index) in {"task", "notes", "interval"}:
                continue

            text_match_count = 0
            rich_text_count = 0
            non_empty_count = 0

            for row in rows:
                if index >= len(row):
                    continue
                cell = " ".join(str(row[index] or "").strip().split())
                if not cell:
                    continue
                non_empty_count += 1
                if looks_like_maintenance_task(cell):
                    text_match_count += 1
                if len(cell.split()) >= 4:
                    rich_text_count += 1

            if text_match_count == 0:
                continue

            score = (text_match_count * 3) + rich_text_count + non_empty_count
            if index in schedule_columns:
                score += 2
            if score > best_score:
                best_score = score
                best_index = index

        return best_index
