from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    AnswerTableSchemaInferer,
)
from src.application.workflows.question_answering.answer_context.tables.projections.answer_table_projection import (
    AnswerTableProjection,
)
from src.application.workflows.question_answering.answer_context.tables.projections.table_projection_support import (
    TableProjectionSupport,
)
from src.application.workflows.question_answering.answer_context.tables.table_header_semantics import (
    active_schedule_labels,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)


class MaintenanceScheduleTableProjectionBuilder:
    def __init__(
        self,
        *,
        schema_inferer: AnswerTableSchemaInferer | None = None,
        projection_support: TableProjectionSupport | None = None,
    ) -> None:
        self.schema_inferer = schema_inferer or AnswerTableSchemaInferer()
        self.projection_support = projection_support or TableProjectionSupport()

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
        table_category: str | None,
        table_shape: str | None,
    ) -> AnswerTableProjection | None:
        if len(cleaned_rows) < 2:
            return None

        headers = self.projection_support.resolve_headers(
            cleaned_rows,
            source.table_header_paths,
        )
        body_rows = cleaned_rows[1:]
        inferred_kind_value, column_roles = self.schema_inferer.infer(
            chunk_type=source.chunk_type,
            headers=headers,
            table_category=table_category,
            table_shape=table_shape,
            rows=body_rows,
        )
        inferred_kind = TableQueryStrategy(inferred_kind_value)
        if inferred_kind not in {
            TableQueryStrategy.MAINTENANCE_SCHEDULE_MATRIX,
            TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE,
        }:
            return None

        normalized_rows = list(
            self._build_rows(
                headers=headers,
                rows=body_rows,
                column_roles=column_roles,
            )
        )
        if not normalized_rows:
            return None

        return AnswerTableProjection(
            headers=["Task", "Interval", "Component", "Notes"],
            body_rows=normalized_rows,
            has_headers=True,
            table_kind=inferred_kind,
            column_roles={
                0: "task",
                1: "interval",
                2: "component",
                3: "notes",
            },
        )

    def _build_rows(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
        column_roles: dict[int, str],
    ):
        task_index = self._index_for_role(column_roles, "task", default=0)
        component_index = self._index_for_role(column_roles, "component")
        notes_index = self._index_for_role(column_roles, "notes")
        direct_interval_index = self._index_for_role(column_roles, "interval")
        marker_interval_indexes = [
            index
            for index, header in enumerate(headers)
            if index != task_index and active_schedule_labels(header=header, cell_value="x")
        ]

        for row in rows:
            task = normalize_cell(row[task_index]) if task_index < len(row) else ""
            if not task:
                continue

            marker_intervals = [
                interval_label
                for index in marker_interval_indexes
                if index < len(row)
                for interval_label in active_schedule_labels(
                    header=headers[index],
                    cell_value=row[index],
                )
            ]
            direct_interval = (
                normalize_cell(row[direct_interval_index])
                if direct_interval_index is not None and direct_interval_index < len(row)
                else ""
            )
            interval = "; ".join(marker_intervals) or direct_interval
            if not interval:
                continue

            component = (
                normalize_cell(row[component_index])
                if component_index is not None and component_index < len(row)
                else ""
            )
            notes = (
                normalize_cell(row[notes_index])
                if notes_index is not None and notes_index < len(row)
                else ""
            )
            yield [task, interval, component, notes]

    @staticmethod
    def _index_for_role(
        column_roles: dict[int, str],
        role_name: str,
        *,
        default: int | None = None,
    ) -> int | None:
        for index, role in column_roles.items():
            if role == role_name:
                return index
        return default
