from __future__ import annotations

from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    MaintenanceCandidate,
    build_description,
    candidate_from_table_row,
    extract_component,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.table_header_semantics import (
    active_schedule_labels,
    schedule_interval_labels,
)
from src.application.workflows.shared.maintenance_text_cleaning import (
    clean_interval,
    clean_optional_text,
)


class MaintenanceTableCandidateExtractor:
    def extract(self, table: AnswerTable) -> list[MaintenanceCandidate]:
        if table.table_kind == "maintenance_schedule_table":
            return list(self._rowwise_candidates(table))
        if table.table_kind == "maintenance_schedule_matrix":
            return list(self._matrix_candidates(table))
        return []

    def _rowwise_candidates(self, table: AnswerTable):
        table_header = self._header_roles(table)
        for row in table.rows:
            candidate = candidate_from_table_row(
                row.cells,
                table_header=table_header,
            )
            if candidate is not None:
                yield candidate

    def _matrix_candidates(self, table: AnswerTable):
        task_index = self._task_column_index(table)
        notes_index = self._optional_column_index(table, "notes")
        component_index = self._optional_column_index(table, "component")
        interval_columns = [
            (index, header)
            for index, header in enumerate(table.headers)
            if schedule_interval_labels(header)
        ]
        for row in table.rows:
            candidate = self._matrix_row_candidate(
                row=row,
                task_index=task_index,
                notes_index=notes_index,
                component_index=component_index,
                interval_columns=interval_columns,
            )
            if candidate is not None:
                yield candidate

    def _matrix_row_candidate(
        self,
        *,
        row: AnswerTableRow,
        task_index: int,
        notes_index: int | None,
        component_index: int | None,
        interval_columns: list[tuple[int, str]],
    ) -> MaintenanceCandidate | None:
        if task_index >= len(row.cells):
            return None
        task = clean_optional_text(row.cells[task_index])
        if task is None:
            return None

        active_intervals = [
            interval_label
            for index, header in interval_columns
            if index < len(row.cells)
            for interval_label in active_schedule_labels(
                header=header,
                cell_value=row.cells[index],
            )
        ]
        if not active_intervals:
            return None

        component = (
            clean_optional_text(row.cells[component_index])
            if component_index is not None and component_index < len(row.cells)
            else None
        )
        if component is None:
            component = extract_component(task)
        notes = (
            clean_optional_text(row.cells[notes_index])
            if notes_index is not None and notes_index < len(row.cells)
            else None
        )
        return MaintenanceCandidate(
            task=task,
            description=build_description(task, notes),
            interval=clean_interval("; ".join(active_intervals)),
            component=component,
            notes=notes,
        )

    @staticmethod
    def _header_roles(table: AnswerTable) -> list[str] | None:
        if not table.headers:
            return None
        roles = [table.column_roles.get(index, "") for index in range(len(table.headers))]
        return roles if any(roles) else None

    @staticmethod
    def _task_column_index(table: AnswerTable) -> int:
        for index, role in table.column_roles.items():
            if role == "task":
                return index
        return 0

    @staticmethod
    def _optional_column_index(table: AnswerTable, role_name: str) -> int | None:
        for index, role in table.column_roles.items():
            if role == role_name:
                return index
        return None
