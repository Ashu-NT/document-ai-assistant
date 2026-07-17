from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    merge_row_cells,
    resolve_sparse_continuation_indexes,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
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
        return bool(
            resolve_sparse_continuation_indexes(
                previous_row,
                current_row,
            )
        )

    def _attach(self, previous_row: list[str], current_row: list[str]) -> list[str]:
        return merge_row_cells(previous_row, current_row)
