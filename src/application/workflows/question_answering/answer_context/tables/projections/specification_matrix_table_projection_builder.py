from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.projections.answer_table_projection import (
    AnswerTableProjection,
)
from src.application.workflows.question_answering.answer_context.tables.projections.table_projection_support import (
    TableProjectionSupport,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.domain.assets.table_rows.table_row_patterns import normalize_cell


class SpecificationMatrixTableProjectionBuilder:
    def __init__(
        self,
        *,
        projection_support: TableProjectionSupport | None = None,
    ) -> None:
        self.projection_support = projection_support or TableProjectionSupport()

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
        table_shape: str | None,
    ) -> AnswerTableProjection | None:
        if table_shape != "specification_matrix" or len(cleaned_rows) < 2:
            return None

        headers = self.projection_support.resolve_headers(
            cleaned_rows,
            source.table_header_paths,
        )
        if len(headers) < 2:
            return None

        normalized_rows = list(
            self._build_rows(
                headers=headers,
                rows=cleaned_rows[1:],
            )
        )
        if not normalized_rows:
            return None

        return AnswerTableProjection(
            headers=["Label", "Value"],
            body_rows=normalized_rows,
            has_headers=True,
            table_kind=TableQueryStrategy.SPECIFICATION_MATRIX,
            column_roles={0: "label", 1: "value"},
        )

    def _build_rows(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
    ):
        label_index = 0
        unit_index = self._unit_index(headers)
        note_index = self._note_index(headers)
        value_indexes = [
            index
            for index in range(1, len(headers))
            if index not in {unit_index, note_index}
        ]
        if not value_indexes:
            return

        multi_field = len(value_indexes) > 1
        for row in rows:
            label = normalize_cell(row[label_index]) if label_index < len(row) else ""
            if not label:
                continue

            unit = row[unit_index] if unit_index is not None and unit_index < len(row) else ""
            notes = (
                normalize_cell(row[note_index])
                if note_index is not None and note_index < len(row)
                else ""
            )
            for index in value_indexes:
                if index >= len(row):
                    continue
                value = self.projection_support.combine_value_with_unit(row[index], unit)
                if not value:
                    continue
                field_header = normalize_cell(headers[index]) if index < len(headers) else ""
                combined_label = self._combined_label(
                    row_label=label,
                    field_header=field_header,
                    multi_field=multi_field,
                )
                if notes:
                    value = f"{value} ({notes})"
                yield [combined_label, value]

    @staticmethod
    def _combined_label(
        *,
        row_label: str,
        field_header: str,
        multi_field: bool,
    ) -> str:
        if not multi_field or not field_header or field_header.casefold() == "value":
            return row_label
        return f"{row_label} ({field_header})"

    @staticmethod
    def _unit_index(headers: list[str]) -> int | None:
        for index, header in enumerate(headers):
            if normalize_cell(header).casefold() == "unit":
                return index
        return None

    @staticmethod
    def _note_index(headers: list[str]) -> int | None:
        for index, header in enumerate(headers):
            normalized = normalize_cell(header).casefold()
            if normalized in {"notes", "remarks"}:
                return index
        return None
