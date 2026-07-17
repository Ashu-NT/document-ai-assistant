from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing.tables.rows.performance_curve_matrix_detector import (
    PerformanceCurveMatrixDetector,
    PerformanceCurveMatrixSpec,
    _looks_numericish,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)


@dataclass(slots=True, frozen=True)
class NormalizedPerformanceCurveMatrix:
    headers: list[str]
    rows: list[list[str]]
    column_roles: dict[int, str]


class PerformanceCurveMatrixNormalizer:
    def __init__(
        self,
        detector: PerformanceCurveMatrixDetector | None = None,
    ) -> None:
        self.detector = detector or PerformanceCurveMatrixDetector()

    def normalize(
        self,
        rows: list[list[str]],
    ) -> NormalizedPerformanceCurveMatrix | None:
        spec = self.detector.detect(rows)
        if spec is None:
            return self._normalize_pre_normalized_rows(rows)

        first_header = rows[0]
        second_header = rows[1]
        headers = self._build_headers(
            first_header=first_header,
            second_header=second_header,
            spec=spec,
        )
        body_rows = self._build_rows(rows=rows[2:], spec=spec)
        if not body_rows:
            return None

        return NormalizedPerformanceCurveMatrix(
            headers=headers,
            rows=body_rows,
            column_roles=self._build_column_roles(spec, len(headers)),
        )

    def _normalize_pre_normalized_rows(
        self,
        rows: list[list[str]],
    ) -> NormalizedPerformanceCurveMatrix | None:
        if len(rows) < 2:
            return None

        headers = [_cell(rows[0], index) for index in range(len(rows[0]))]
        metric_index = self._metric_index(headers)
        if metric_index is None:
            return None
        if metric_index < 1 or len(headers) - metric_index - 1 < 3:
            return None

        body_rows = [list(row) for row in rows[1:] if any(_cell(row, i) for i in range(len(row)))]
        if not body_rows:
            return None
        sample_row = body_rows[0]
        data_points = [
            _cell(sample_row, column_index)
            for column_index in range(metric_index + 1, len(headers))
        ]
        if sum(1 for value in data_points if _looks_numericish(value)) < 3:
            return None

        descriptor_indexes = tuple(range(metric_index))
        return NormalizedPerformanceCurveMatrix(
            headers=headers,
            rows=body_rows,
            column_roles=self._build_pre_normalized_column_roles(
                metric_index=metric_index,
                header_count=len(headers),
            ),
        )

    def _build_headers(
        self,
        *,
        first_header: list[str],
        second_header: list[str],
        spec: PerformanceCurveMatrixSpec,
    ) -> list[str]:
        headers: list[str] = []
        for column_index in spec.descriptor_indexes:
            headers.append(
                self._merge_descriptor_header(
                    _cell(first_header, column_index),
                    _cell(second_header, column_index),
                )
            )

        headers.append("Curve metric")
        primary_axis_label = _cell(first_header, spec.metric_index)
        secondary_axis_label = _cell(second_header, spec.metric_index)
        for column_index in range(spec.data_start_index, max(len(first_header), len(second_header))):
            headers.append(
                self._build_curve_value_header(
                    primary_axis_label=primary_axis_label,
                    secondary_axis_label=secondary_axis_label,
                    primary_value=_cell(first_header, column_index),
                    secondary_value=_cell(second_header, column_index),
                )
            )
        return headers

    def _build_rows(
        self,
        *,
        rows: list[list[str]],
        spec: PerformanceCurveMatrixSpec,
    ) -> list[list[str]]:
        normalized_rows: list[list[str]] = []
        for row in rows:
            descriptor_cells = [
                _cell(row, column_index) for column_index in spec.descriptor_indexes
            ]
            metric_value = _cell(row, spec.metric_index)
            data_values = [
                _cell(row, column_index)
                for column_index in range(spec.data_start_index, len(row))
            ]
            if sum(1 for value in data_values if value) < 3:
                continue
            normalized_rows.append([*descriptor_cells, metric_value, *data_values])
        return normalized_rows

    @staticmethod
    def _build_column_roles(
        spec: PerformanceCurveMatrixSpec,
        header_count: int,
    ) -> dict[int, str]:
        roles: dict[int, str] = {}
        if spec.descriptor_indexes:
            roles[spec.descriptor_indexes[0]] = "series"
        for column_index in spec.descriptor_indexes[1:]:
            roles[column_index] = "descriptor"
        metric_index = len(spec.descriptor_indexes)
        roles[metric_index] = "curve_metric"
        for column_index in range(metric_index + 1, header_count):
            roles[column_index] = "curve_point"
        return roles

    @staticmethod
    def _build_pre_normalized_column_roles(
        *,
        metric_index: int,
        header_count: int,
    ) -> dict[int, str]:
        roles: dict[int, str] = {}
        if metric_index >= 1:
            roles[0] = "series"
        for column_index in range(1, metric_index):
            roles[column_index] = "descriptor"
        roles[metric_index] = "curve_metric"
        for column_index in range(metric_index + 1, header_count):
            roles[column_index] = "curve_point"
        return roles

    @staticmethod
    def _merge_descriptor_header(primary: str, secondary: str) -> str:
        if not primary and not secondary:
            return "Descriptor"
        if not primary:
            return secondary
        if not secondary or secondary.casefold() == primary.casefold():
            return primary
        if secondary.casefold() in {"kw", "hp", "a", "v", "hz", "mm", "bar"}:
            return f"{primary} ({secondary})"
        if primary.casefold() in secondary.casefold():
            return secondary
        if secondary.casefold() in primary.casefold():
            return primary
        return f"{primary} / {secondary}"

    @staticmethod
    def _build_curve_value_header(
        *,
        primary_axis_label: str,
        secondary_axis_label: str,
        primary_value: str,
        secondary_value: str,
    ) -> str:
        primary_label = _combine_axis_and_value(primary_axis_label, primary_value)
        secondary_label = _combine_axis_and_value(secondary_axis_label, secondary_value)
        if primary_label and secondary_label and primary_label != secondary_label:
            return f"{primary_label} / {secondary_label}"
        return primary_label or secondary_label or "Curve value"

    @staticmethod
    def _metric_index(headers: list[str]) -> int | None:
        for index, header in enumerate(headers):
            if header.casefold() == "curve metric":
                return index
        return None


def _cell(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return normalize_cell(row[index])


def _combine_axis_and_value(axis_label: str, value: str) -> str:
    cleaned_axis = normalize_cell(axis_label)
    cleaned_value = normalize_cell(value)
    if cleaned_axis and cleaned_value:
        return f"{cleaned_axis} {cleaned_value}"
    return cleaned_axis or cleaned_value
