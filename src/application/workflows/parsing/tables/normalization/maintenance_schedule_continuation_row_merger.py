from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    merge_row_cells,
)
from src.application.workflows.parsing.tables.rows.span_aware_row_continuation_resolver import (
    SpanAwareRowContinuationResolver,
)
from src.domain.assets.table_cell_span import TableCellSpan


class MaintenanceScheduleContinuationRowMerger:
    """Conservatively repairs schedule rows only when Docling provides
    direct vertical span evidence.

    Maintenance matrices often wrap the task or notes column while the
    interval markers remain on the first physical row. In those cases
    the generic continuation resolver is too anchor-oriented because the
    wrapped text may live in the first column itself. This merger uses
    span-backed proof with no fixed anchor column so task-first schedule
    layouts can be reconstructed safely.
    """

    def __init__(
        self,
        *,
        span_aware_resolver: SpanAwareRowContinuationResolver | None = None,
    ) -> None:
        self.span_aware_resolver = span_aware_resolver or SpanAwareRowContinuationResolver()

    def merge(
        self,
        rows: list[list[str]],
        *,
        cell_spans: list[TableCellSpan] | None,
    ) -> list[list[str]]:
        if not cell_spans or len(rows) < 3:
            return rows

        merged_rows: list[list[str]] = [list(rows[0])]
        merged_source_row_indexes: list[int] = [0]

        for current_row_index, row in enumerate(rows[1:], start=1):
            if len(merged_rows) == 1:
                merged_rows.append(list(row))
                merged_source_row_indexes.append(current_row_index)
                continue

            previous_source_row_index = merged_source_row_indexes[-1]
            continuation_indexes = self.span_aware_resolver.resolve(
                merged_rows[-1],
                row,
                previous_row_index=previous_source_row_index,
                current_row_index=current_row_index,
                cell_spans=cell_spans,
                anchor_indexes=frozenset(),
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
