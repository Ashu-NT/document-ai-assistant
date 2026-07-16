from __future__ import annotations

from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)

class PerformanceCurveTableNormalizer:
    def __init__(
        self,
        *,
        matrix_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.matrix_normalizer = matrix_normalizer or PerformanceCurveMatrixNormalizer()

    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        del cell_spans, chunk_type, table_category
        normalized = self.matrix_normalizer.normalize(rows)
        if normalized is None:
            return None
        return NormalizedTableRows(
            headers=list(normalized.headers),
            rows=[list(row) for row in normalized.rows],
        )
