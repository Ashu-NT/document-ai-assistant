from __future__ import annotations

from src.application.workflows.parsing.tables.normalization.performance_curve.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets import TableAsset


class TableShapeResolver:
    def __init__(
        self,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveMatrixNormalizer()
        )

    def resolve(self, table: TableAsset) -> str | None:
        if table.table_shape:
            return table.table_shape
        if self.performance_curve_normalizer.normalize(table.rows) is not None:
            return "performance_curve_matrix"
        return None
