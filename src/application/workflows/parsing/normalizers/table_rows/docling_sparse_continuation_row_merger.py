from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_index_resolver import (
    RowContinuationIndexResolver,
)
from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    merge_row_cells,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)
from src.domain.assets import TableCellSpan


class DoclingSparseContinuationRowMerger:
    """Attaches sparse subordinate rows to the most recent compatible row."""

    def __init__(
        self,
        *,
        continuation_index_resolver: RowContinuationIndexResolver | None = None,
    ) -> None:
        self.continuation_index_resolver = (
            continuation_index_resolver or RowContinuationIndexResolver()
        )

    def merge(
        self,
        rows: list[list[str]],
        *,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> list[list[str]]:
        if len(rows) < 2:
            return rows

        merged_rows: list[list[str]] = []
        for row_index, row in enumerate(rows):
            normalized_row = [normalize_cell(cell) for cell in row]
            if not merged_rows:
                merged_rows.append(normalized_row)
                continue

            previous_row = merged_rows[-1]
            continuation_indexes = self._resolve_continuation_indexes(
                previous_row,
                normalized_row,
                previous_row_index=row_index - 1,
                current_row_index=row_index,
                cell_spans=cell_spans,
            )
            if not continuation_indexes:
                merged_rows.append(normalized_row)
                continue

            merged_rows[-1] = self._attach(
                previous_row,
                normalized_row,
                indexes=continuation_indexes,
            )
        return merged_rows

    def _resolve_continuation_indexes(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        previous_row_index: int,
        current_row_index: int,
        cell_spans: list[TableCellSpan] | None,
    ) -> list[int]:
        return self.continuation_index_resolver.resolve(
            previous_row,
            current_row,
            previous_row_index=previous_row_index,
            current_row_index=current_row_index,
            cell_spans=cell_spans,
        )

    def _attach(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        indexes: list[int],
    ) -> list[str]:
        return merge_row_cells(previous_row, current_row, indexes=indexes)
