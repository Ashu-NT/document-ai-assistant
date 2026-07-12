from __future__ import annotations

from typing import Sequence

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_schema_inferer import (
    AnswerTableSchemaInferer,
)


class AnswerTableProjector:
    def __init__(
        self,
        schema_inferer: AnswerTableSchemaInferer | None = None,
    ) -> None:
        self.schema_inferer = schema_inferer or AnswerTableSchemaInferer()

    def build(self, sources: Sequence[AnswerSource]) -> list[AnswerTable]:
        tables: list[AnswerTable] = []
        for source in sources:
            if not source.table_rows:
                continue
            table = self._build_table(source)
            if table is not None:
                tables.append(table)
        return tables

    def _build_table(self, source: AnswerSource) -> AnswerTable | None:
        cleaned_rows = [self._clean_row(row) for row in source.table_rows or []]
        cleaned_rows = [row for row in cleaned_rows if row]
        if not cleaned_rows:
            return None

        has_headers = self._has_header_row(cleaned_rows)
        headers = cleaned_rows[0] if has_headers else []
        body_rows = cleaned_rows[1:] if has_headers else cleaned_rows
        table_kind, column_roles = self.schema_inferer.infer(
            chunk_type=source.chunk_type,
            headers=headers,
        )
        rows = [
            AnswerTableRow(
                source_row_index=source_row_index,
                cells=list(row),
                cells_by_header=self._cells_by_header(headers, row),
            )
            for source_row_index, row in enumerate(
                body_rows,
                start=1 if has_headers else 0,
            )
        ]
        if not rows and not headers:
            return None

        return AnswerTable(
            source_number=source.source_number,
            chunk_id=source.chunk_id,
            chunk_type=source.chunk_type,
            document_title=source.document_title,
            section_path=source.section_path,
            page_start=source.page_start,
            page_end=source.page_end,
            headers=headers,
            rows=rows,
            table_kind=table_kind,
            column_roles=column_roles,
        )

    @staticmethod
    def _clean_row(row: list[str]) -> list[str]:
        normalized = [" ".join(str(cell or "").split()).strip() for cell in row]
        return normalized if any(normalized) else []

    def _has_header_row(self, rows: list[list[str]]) -> bool:
        if len(rows) < 2:
            return False
        header = rows[0]
        if len(header) < 2:
            return False
        lowered = [cell.lower() for cell in header if cell]
        if len(lowered) != len(header):
            return False
        if len(set(lowered)) != len(lowered):
            return False
        numeric_like = sum(1 for cell in header if self._looks_numeric(cell))
        return numeric_like < max(1, len(header) // 2)

    @staticmethod
    def _cells_by_header(headers: list[str], row: list[str]) -> dict[str, str]:
        if not headers:
            return {}
        return {
            header: row[index]
            for index, header in enumerate(headers)
            if header and index < len(row) and row[index]
        }

    @staticmethod
    def _looks_numeric(value: str) -> bool:
        stripped = value.strip().replace(",", "").replace(".", "").replace("-", "")
        return bool(stripped) and stripped.isdigit()
