from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.projections.answer_table_projection import (
    AnswerTableProjection,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
)
from src.application.workflows.parsing.tables.normalization.troubleshooting_table_normalizer import (
    TroubleshootingTableNormalizer,
)


class TroubleshootingTableProjectionBuilder:
    def __init__(
        self,
        *,
        troubleshooting_table_normalizer: (
            TroubleshootingTableNormalizer | None
        ) = None,
    ) -> None:
        self.troubleshooting_table_normalizer = (
            troubleshooting_table_normalizer or TroubleshootingTableNormalizer()
        )

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
        table_category: str | None,
    ) -> AnswerTableProjection | None:
        normalized = self.troubleshooting_table_normalizer.normalize(
            cleaned_rows,
            table_category=table_category,
            chunk_type=source.chunk_type,
        )
        if normalized is None:
            return None

        column_roles = {
            index: header.strip().lower()
            for index, header in enumerate(normalized.headers)
            if header.strip()
        }
        return AnswerTableProjection(
            headers=normalized.headers,
            body_rows=normalized.rows,
            has_headers=True,
            table_kind=TableQueryStrategy.TROUBLESHOOTING_TABLE,
            column_roles=column_roles,
        )
