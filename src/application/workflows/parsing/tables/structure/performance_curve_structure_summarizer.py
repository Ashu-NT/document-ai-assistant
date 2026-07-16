from __future__ import annotations

from src.application.workflows.parsing.tables.structure.table_structure_summary import (
    TableStructureSummary,
)
from src.application.workflows.shared.table_shape import TableShape
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets.table_rows.table_row_patterns import normalize_cell


class PerformanceCurveStructureSummarizer:
    def __init__(
        self,
        *,
        row_canonicalizer: TableRowCanonicalizer | None = None,
        normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()
        self.normalizer = normalizer or PerformanceCurveMatrixNormalizer()

    def summarize(self, rows: list[list[str]]) -> TableStructureSummary | None:
        cleaned_rows = self.row_canonicalizer.canonicalize(rows)
        normalized = self.normalizer.normalize(cleaned_rows)
        if normalized is None:
            return None

        header_paths = self._header_paths(cleaned_rows, normalized.headers)
        quality_score = self._quality_score(normalized.rows, normalized.headers)
        return TableStructureSummary(
            table_shape=TableShape.PERFORMANCE_CURVE_MATRIX,
            quality_score=quality_score,
            header_paths=header_paths,
            axis_summary={
                "row_axis": "series",
                "column_axis": "curve_point",
                "value_axis": "numeric_measurement",
                "descriptor_axis": "curve_metric",
            },
        )

    def _header_paths(
        self,
        rows: list[list[str]],
        normalized_headers: list[str],
    ) -> list[list[str]]:
        del rows
        return [self._normalized_header_path(header) for header in normalized_headers]

    @staticmethod
    def _normalized_header_path(header: str) -> list[str]:
        normalized_header = normalize_cell(header)
        if not normalized_header:
            return []
        if " / " in normalized_header:
            return [part for part in normalized_header.split(" / ") if part]
        if normalized_header.endswith(")") and " (" in normalized_header:
            prefix, suffix = normalized_header[:-1].split(" (", maxsplit=1)
            return [prefix, suffix]
        return [normalized_header]

    @staticmethod
    def _quality_score(rows: list[list[str]], headers: list[str]) -> float:
        non_empty_data_points = sum(
            1
            for row in rows
            for cell in row
            if normalize_cell(cell)
        )
        header_strength = min(1.0, len([header for header in headers if header]) / 6)
        data_strength = min(1.0, non_empty_data_points / 18)
        score = 0.55 + (header_strength * 0.2) + (data_strength * 0.25)
        return round(min(score, 0.98), 2)
