from __future__ import annotations

from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets.table_rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.domain.assets.table_rows.table_row_patterns import (
    active_interval_labels,
    count_boolean_markers,
    count_interval_columns,
    dedupe_headers,
    looks_interval_header,
    normalize_cell,
)


class StructuredRowRenderer:
    def __init__(
        self,
        canonicalizer: TableRowCanonicalizer | None = None,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.canonicalizer = canonicalizer or TableRowCanonicalizer()
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveMatrixNormalizer()
        )

    def render(self, rows: list[list[str]]) -> str | None:
        cleaned_rows = self.canonicalizer.canonicalize(rows)
        if len(cleaned_rows) < 2:
            return None
        if self._looks_schedule_matrix(cleaned_rows):
            return self._render_schedule_matrix(cleaned_rows)
        performance_curve = self.performance_curve_normalizer.normalize(cleaned_rows)
        if performance_curve is not None:
            return self._render_labeled_rows(
                headers=performance_curve.headers,
                rows=performance_curve.rows,
            )

        return self._render_labeled_rows(
            headers=dedupe_headers(cleaned_rows[0]),
            rows=cleaned_rows[1:],
        )

    def _looks_schedule_matrix(self, rows: list[list[str]]) -> bool:
        headers = [normalize_cell(cell) for cell in rows[0]]
        interval_columns = {
            index for index, header in enumerate(headers) if looks_interval_header(header)
        }
        if len(interval_columns) < 2:
            return False
        positives, inspected = count_boolean_markers(
            rows[1:],
            column_indexes=interval_columns,
        )
        if inspected == 0:
            return False
        return positives / inspected >= 0.5 and count_interval_columns(headers) >= 2

    def _render_schedule_matrix(self, rows: list[list[str]]) -> str | None:
        headers = [normalize_cell(cell) for cell in rows[0]]
        interval_columns = {
            index for index, header in enumerate(headers) if looks_interval_header(header)
        }
        descriptive_columns = [
            index for index in range(len(headers)) if index not in interval_columns
        ]

        lines: list[str] = []
        for row_index, row in enumerate(rows[1:], start=1):
            active_labels = active_interval_labels(headers, row)
            descriptive_cells = [
                normalize_cell(row[index])
                for index in descriptive_columns
                if index < len(row) and normalize_cell(row[index])
            ]
            if not active_labels and not descriptive_cells:
                continue

            primary = max(descriptive_cells, key=len) if descriptive_cells else ""
            secondary = [
                cell for cell in descriptive_cells if cell and cell != primary
            ]

            rendered_cells: list[str] = []
            if primary:
                rendered_cells.append(f"Task={primary}")
            if active_labels:
                rendered_cells.append(f"Intervals={', '.join(active_labels)}")
            if secondary:
                rendered_cells.append(f"Details={' | '.join(secondary)}")
            if rendered_cells:
                lines.append(f"Row {row_index}: " + " | ".join(rendered_cells))

        if not lines:
            return None
        return "\n".join(lines)

    @staticmethod
    def _render_labeled_rows(
        *,
        headers: list[str],
        rows: list[list[str]],
    ) -> str | None:
        lines: list[str] = []
        for row_index, row in enumerate(rows, start=1):
            rendered_cells = [
                f"{headers[column_index]}={normalize_cell(cell)}"
                for column_index, cell in enumerate(row)
                if column_index < len(headers)
                and headers[column_index]
                and normalize_cell(cell)
            ]
            if rendered_cells:
                lines.append(f"Row {row_index}: " + " | ".join(rendered_cells))
        if not lines:
            return None
        return "\n".join(lines)
