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
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)


class GenericTableProjectionBuilder:
    def __init__(
        self,
        *,
        schema_inferer: AnswerTableSchemaInferer | None = None,
        row_canonicalizer: TableRowCanonicalizer | None = None,
    ) -> None:
        self.schema_inferer = schema_inferer or AnswerTableSchemaInferer()
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
        table_category: str | None,
        table_shape: str | None,
    ) -> AnswerTableProjection:
        has_headers = self.row_canonicalizer.has_explicit_header_row(cleaned_rows)
        headers = cleaned_rows[0] if has_headers else []
        body_rows = cleaned_rows[1:] if has_headers else cleaned_rows
        table_kind, column_roles = self.schema_inferer.infer(
            chunk_type=source.chunk_type,
            headers=headers,
            table_category=table_category,
            table_shape=table_shape,
            rows=body_rows,
        )
        return AnswerTableProjection(
            headers=headers,
            body_rows=body_rows,
            has_headers=has_headers,
            table_kind=table_kind,
            column_roles=column_roles,
        )
