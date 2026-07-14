from __future__ import annotations

from src.domain.assets import TableAsset
from src.domain.assets.table_rows.performance_curve_matrix_normalizer import (
    PerformanceCurveMatrixNormalizer,
)
from src.domain.assets.table_rows.table_row_patterns import normalize_cell


class PerformanceCurvePayloadBuilder:
    def __init__(
        self,
        *,
        performance_curve_normalizer: PerformanceCurveMatrixNormalizer | None = None,
    ) -> None:
        self.performance_curve_normalizer = (
            performance_curve_normalizer or PerformanceCurveMatrixNormalizer()
        )

    def build(self, table: TableAsset, *, chunk_type: str | None = None) -> str | None:
        if table.resolved_table_shape() not in {None, "", "performance_curve_matrix"}:
            return None

        normalized = self.performance_curve_normalizer.normalize(table.rows)
        if normalized is None:
            return None

        metric_index = next(
            (
                index
                for index, role in normalized.column_roles.items()
                if role == "curve_metric"
            ),
            0,
        )
        lines: list[str] = []
        for row_index, row in enumerate(normalized.rows, start=1):
            descriptor_fields = [
                f"{normalized.headers[index]}={normalize_cell(row[index])}"
                for index in range(metric_index)
                if index < len(row)
                and normalize_cell(normalized.headers[index])
                and normalize_cell(row[index])
            ]
            metric_value = normalize_cell(row[metric_index]) if metric_index < len(row) else ""
            point_fields = [
                f"{normalized.headers[index]}={normalize_cell(row[index])}"
                for index in range(metric_index + 1, min(len(normalized.headers), len(row)))
                if normalize_cell(normalized.headers[index]) and normalize_cell(row[index])
            ]
            rendered_fields = descriptor_fields
            if metric_value:
                rendered_fields.append(
                    f"{normalized.headers[metric_index]}={metric_value}"
                )
            if point_fields:
                rendered_fields.append("Curve points=" + "; ".join(point_fields))
            if rendered_fields:
                lines.append(f"Row {row_index}: " + " | ".join(rendered_fields))

        if not lines:
            return None
        return "Structured performance data:\n" + "\n".join(lines)
