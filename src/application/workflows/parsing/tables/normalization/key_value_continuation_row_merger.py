from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_index_resolver import (
    RowContinuationIndexResolver,
)
from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    merge_row_cells,
)
from src.domain.assets.table_cell_span import TableCellSpan


class KeyValueContinuationRowMerger:
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
        cell_spans: list[TableCellSpan] | None,
    ) -> list[list[str]]:
        if not cell_spans or len(rows) < 2:
            return rows

        merged_rows: list[list[str]] = [list(rows[0])]
        merged_source_row_indexes: list[int] = [0]
        for current_row_index, row in enumerate(rows[1:], start=1):
            previous_source_row_index = merged_source_row_indexes[-1]
            continuation_indexes = self.continuation_index_resolver.resolve(
                merged_rows[-1],
                row,
                max_non_empty_cells=None,
                previous_row_index=previous_source_row_index,
                current_row_index=current_row_index,
                cell_spans=cell_spans,
            )
            if not continuation_indexes:
                merged_rows.append(list(row))
                merged_source_row_indexes.append(current_row_index)
                continue
            merged_rows[-1] = merge_row_cells(
                merged_rows[-1],
                row,
                indexes=continuation_indexes,
            )
            merged_source_row_indexes[-1] = current_row_index
        return merged_rows
