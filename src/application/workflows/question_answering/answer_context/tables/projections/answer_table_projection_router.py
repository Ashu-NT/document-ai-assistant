from __future__ import annotations

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)
from src.application.workflows.question_answering.answer_context.tables.projections.answer_table_projection import (
    AnswerTableProjection,
)
from src.application.workflows.question_answering.answer_context.tables.projections.generic_table_projection_builder import (
    GenericTableProjectionBuilder,
)
from src.application.workflows.question_answering.answer_context.tables.projections.performance_curve_table_projection_builder import (
    PerformanceCurveTableProjectionBuilder,
)
from src.application.workflows.question_answering.answer_context.tables.projections.spare_parts_table_projection_builder import (
    SparePartsTableProjectionBuilder,
)


class AnswerTableProjectionRouter:
    def __init__(
        self,
        *,
        spare_parts_projection_builder: SparePartsTableProjectionBuilder | None = None,
        performance_curve_projection_builder: (
            PerformanceCurveTableProjectionBuilder | None
        ) = None,
        generic_projection_builder: GenericTableProjectionBuilder | None = None,
    ) -> None:
        self.spare_parts_projection_builder = (
            spare_parts_projection_builder or SparePartsTableProjectionBuilder()
        )
        self.performance_curve_projection_builder = (
            performance_curve_projection_builder
            or PerformanceCurveTableProjectionBuilder()
        )
        self.generic_projection_builder = (
            generic_projection_builder or GenericTableProjectionBuilder()
        )

    def project(
        self,
        *,
        source: AnswerSource,
        cleaned_rows: list[list[str]],
    ) -> AnswerTableProjection | None:
        table_category = source.metadata.get("table_category")
        table_shape = source.table_shape or source.metadata.get("table_shape")

        spare_parts_projection = self.spare_parts_projection_builder.project(
            source=source,
            cleaned_rows=cleaned_rows,
            table_category=table_category,
            table_shape=table_shape,
        )
        if spare_parts_projection is not None:
            return spare_parts_projection

        performance_curve_projection = (
            self.performance_curve_projection_builder.project(
                cleaned_rows=cleaned_rows,
                table_shape=table_shape,
            )
        )
        if performance_curve_projection is not None:
            return performance_curve_projection

        return self.generic_projection_builder.project(
            source=source,
            cleaned_rows=cleaned_rows,
            table_category=table_category,
            table_shape=table_shape,
        )
