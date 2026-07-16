from __future__ import annotations

from src.domain.assets.table_rows.table_row_patterns import (
    looks_continuation_start,
    looks_incomplete_text,
    looks_terminated_text,
    merge_continuation_text,
    normalize_cell,
)


class DoclingSparseContinuationRowMerger:
    """Attaches sparse subordinate rows to the most recent compatible row."""

    def merge(self, rows: list[list[str]]) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        merged_rows: list[list[str]] = []
        for row in rows:
            normalized_row = [normalize_cell(cell) for cell in row]
            if not merged_rows:
                merged_rows.append(normalized_row)
                continue

            previous_row = merged_rows[-1]
            if not self._should_attach(previous_row, normalized_row):
                merged_rows.append(normalized_row)
                continue

            merged_rows[-1] = self._attach(previous_row, normalized_row)
        return merged_rows

    def _should_attach(self, previous_row: list[str], current_row: list[str]) -> bool:
        current_indexes = self._non_empty_indexes(current_row)
        if not current_indexes or current_indexes[0] == 0:
            return False
        if any(
            index >= len(previous_row) or not normalize_cell(previous_row[index])
            for index in current_indexes
        ):
            return False
        return any(
            self._looks_like_continuation(previous_row[index], current_row[index])
            for index in current_indexes
        )

    @staticmethod
    def _non_empty_indexes(row: list[str]) -> list[int]:
        return [index for index, value in enumerate(row) if normalize_cell(value)]

    def _looks_like_continuation(self, previous_value: str, current_value: str) -> bool:
        previous = normalize_cell(previous_value)
        current = normalize_cell(current_value)
        if not previous or not current:
            return False
        if previous.casefold() == current.casefold():
            return False
        if previous.endswith("-"):
            return True
        if looks_incomplete_text(previous):
            return True
        return not looks_terminated_text(previous) and looks_continuation_start(current)

    def _attach(self, previous_row: list[str], current_row: list[str]) -> list[str]:
        merged = list(previous_row)
        for index, value in enumerate(current_row):
            normalized = normalize_cell(value)
            if not normalized:
                continue
            merged[index] = merge_continuation_text(merged[index], normalized)
        return merged
