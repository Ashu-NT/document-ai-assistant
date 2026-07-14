from __future__ import annotations

from src.application.workflows.question_answering.answer_context.tables.projections.answer_table_projection import (
    AnswerTableProjection,
)
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)


class PerformanceCurveTableProjectionBuilder:
    def __init__(
        self,
        *,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveMatrixNormalizer()
        )

    def project(
        self,
        *,
        cleaned_rows: list[list[str]],
        table_shape: str | None,
    ) -> AnswerTableProjection | None:
        if table_shape not in {None, "", "performance_curve_matrix"}:
            return None

        normalized = self.performance_curve_normalizer.normalize(cleaned_rows)
        if normalized is None:
            return None

        return AnswerTableProjection(
            headers=normalized.headers,
            body_rows=normalized.rows,
            has_headers=True,
            table_kind="performance_curve_matrix",
            column_roles=normalized.column_roles,
        )
