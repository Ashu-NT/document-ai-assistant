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
from src.application.workflows.question_answering.answer_context.tables.spare_parts_table_normalizer import (
    SparePartsTableNormalizer,
)


class SparePartsTableProjectionBuilder:
    def __init__(
        self,
        *,
        spare_parts_table_normalizer: SparePartsTableNormalizer | None = None,
        schema_inferer: AnswerTableSchemaInferer | None = None,
    ) -> None:
        self.spare_parts_table_normalizer = (
            spare_parts_table_normalizer or SparePartsTableNormalizer()
        )
        self.schema_inferer = schema_inferer or AnswerTableSchemaInferer()

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
        table_category: str | None,
        table_shape: str | None,
    ) -> AnswerTableProjection | None:
        normalized = self.spare_parts_table_normalizer.normalize(
            cleaned_rows,
            table_category=table_category,
            chunk_type=source.chunk_type,
        )
        if normalized is None:
            return None

        headers = normalized.headers
        body_rows = normalized.rows
        _, column_roles = self.schema_inferer.infer(
            chunk_type=source.chunk_type,
            headers=headers,
            table_category=table_category,
            table_shape=table_shape,
            rows=body_rows,
        )
        return AnswerTableProjection(
            headers=headers,
            body_rows=body_rows,
            has_headers=True,
            table_kind="record_table",
            column_roles=column_roles,
        )
