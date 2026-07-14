from __future__ import annotations

from dataclasses import dataclass

from src.domain.assets.table_rows.table_row_patterns import normalize_cell


@dataclass(slots=True, frozen=True)
class PerformanceCurveMatrixSpec:
    descriptor_indexes: tuple[int, ...]
    metric_index: int
    data_start_index: int


_MAX_SAMPLE_ROW_CANDIDATES = 5


class PerformanceCurveMatrixDetector:
    def detect(self, rows: list[list[str]]) -> PerformanceCurveMatrixSpec | None:
        if len(rows) < 3:
            return None

        first_header = rows[0]
        second_header = rows[1]
        sample_row_candidates = rows[2 : 2 + _MAX_SAMPLE_ROW_CANDIDATES]
        max_width = max(
            len(first_header),
            len(second_header),
            *(len(row) for row in sample_row_candidates),
        )
        if max_width < 5:
            return None

        for start_index in range(2, max_width - 2):
            # A single sparse data row (a sensor reading not taken at
            # one point, a trailing blank cell) shouldn't sink detection
            # for the whole table - try a few candidate rows before
            # giving up on this start_index.
            for sample_row in sample_row_candidates:
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
        both_numeric_pairs = 0
        both_numeric_pairs_differ = 0

        for column_index in range(start_index, max(len(first_header), len(second_header))):
            top_value = _cell(first_header, column_index)
            bottom_value = _cell(second_header, column_index)
            sample_value = _cell(sample_row, column_index)

            if not sample_value:
                break

            if not self._looks_like_curve_axis_point(top_value, bottom_value):
                break
            inspected_cells += 1
            if not _looks_numericish(sample_value):
                break
            if _looks_numericish(top_value) and _looks_numericish(bottom_value):
                both_numeric_pairs += 1
                if top_value != bottom_value:
                    both_numeric_pairs_differ += 1

            consecutive_numeric_columns += 1
            numeric_cells += 1

        if consecutive_numeric_columns < 3:
            return False
        if inspected_cells == 0:
            return False
        if both_numeric_pairs > 0 and both_numeric_pairs_differ == 0:
            # Every dual-numeric header column repeats the identical value
            # in both rows - a genuine curve axis point is the same
            # physical point in two different units (e.g. "1"/"16.6"),
            # so at least one column should show a real conversion. All
            # columns matching exactly means this is a discrete numeric
            # variant/size axis (e.g. bolt diameters 6/8/10/12mm) that
            # happens to appear on both header rows, not a curve.
            return False
        return numeric_cells / inspected_cells >= 0.6

    @staticmethod
    def _looks_like_curve_axis_point(top_value: str, bottom_value: str) -> bool:
        """A curve data column's two header cells are the same axis point
        expressed in two units (e.g. "0"/"0", "1"/"16.6") - both numeric,
        or one numeric with the other left blank by a merged header cell.

        A non-blank, non-numeric header cell (e.g. a size/variant code
        like "A"/"B"/"C") means this is a labeled variant column, not a
        curve axis point, even if the other header row happens to be
        numeric - that shape belongs to a specification/dimension table,
        not a performance curve matrix.
        """
        top_is_numeric = _looks_numericish(top_value)
        bottom_is_numeric = _looks_numericish(bottom_value)
        if not top_is_numeric and top_value:
            return False
        if not bottom_is_numeric and bottom_value:
            return False
        return top_is_numeric or bottom_is_numeric

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
