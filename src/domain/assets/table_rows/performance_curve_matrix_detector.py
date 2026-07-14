from __future__ import annotations

from dataclasses import dataclass

from src.domain.assets.table_rows.table_row_patterns import normalize_cell


@dataclass(slots=True, frozen=True)
class PerformanceCurveMatrixSpec:
    descriptor_indexes: tuple[int, ...]
    metric_index: int
    data_start_index: int


class PerformanceCurveMatrixDetector:
    def detect(self, rows: list[list[str]]) -> PerformanceCurveMatrixSpec | None:
        if len(rows) < 3:
            return None

        first_header = rows[0]
        second_header = rows[1]
        sample_row = rows[2]
        max_width = max(len(first_header), len(second_header), len(sample_row))
        if max_width < 5:
            return None

        for start_index in range(2, max_width - 2):
            if not self._has_curve_block(
                first_header=first_header,
                second_header=second_header,
                sample_row=sample_row,
                start_index=start_index,
            ):
                continue

            metric_index = start_index - 1
            if metric_index < 1:
                continue
            if not self._has_descriptor_signal(
                first_header=first_header,
                second_header=second_header,
                metric_index=metric_index,
            ):
                continue

            descriptor_indexes = tuple(range(metric_index))
            return PerformanceCurveMatrixSpec(
                descriptor_indexes=descriptor_indexes,
                metric_index=metric_index,
                data_start_index=start_index,
            )
        return None

    def _has_curve_block(
        self,
        *,
        first_header: list[str],
        second_header: list[str],
        sample_row: list[str],
        start_index: int,
    ) -> bool:
        consecutive_numeric_columns = 0
        numeric_cells = 0
        inspected_cells = 0

        for column_index in range(start_index, max(len(first_header), len(second_header))):
            top_value = _cell(first_header, column_index)
            bottom_value = _cell(second_header, column_index)
            sample_value = _cell(sample_row, column_index)

            if not sample_value:
                break

            header_numeric = _looks_numericish(top_value) or _looks_numericish(bottom_value)
            inspected_cells += 1
            if not header_numeric or not _looks_numericish(sample_value):
                break

            consecutive_numeric_columns += 1
            numeric_cells += 1

        if consecutive_numeric_columns < 3:
            return False
        if inspected_cells == 0:
            return False
        return numeric_cells / inspected_cells >= 0.6

    def _has_descriptor_signal(
        self,
        *,
        first_header: list[str],
        second_header: list[str],
        metric_index: int,
    ) -> bool:
        descriptor_labels = 0
        for column_index in range(metric_index):
            top_value = _cell(first_header, column_index)
            bottom_value = _cell(second_header, column_index)
            if _looks_textual_header(top_value) or _looks_textual_header(bottom_value):
                descriptor_labels += 1
        return descriptor_labels >= 1 and (
            _looks_textual_header(_cell(first_header, metric_index))
            or _looks_textual_header(_cell(second_header, metric_index))
        )


def _cell(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return normalize_cell(row[index])


def _looks_numericish(value: str) -> bool:
    cleaned = normalize_cell(value)
    if not cleaned:
        return False
    candidate = cleaned.replace(",", "").replace(" ", "")
    candidate = candidate.replace("%", "").replace("°", "")
    candidate = candidate.replace("≤", "").replace("≥", "")
    candidate = candidate.replace("<", "").replace(">", "")
    candidate = candidate.replace("+/-", "").replace("±", "")
    candidate = candidate.replace("/", "")
    candidate = candidate.replace("-", "", 1)
    candidate = candidate.replace(".", "", 1)
    return candidate.isdigit()


def _looks_textual_header(value: str) -> bool:
    cleaned = normalize_cell(value)
    if not cleaned:
        return False
    if _looks_numericish(cleaned):
        return False
    return any(character.isalpha() for character in cleaned)
