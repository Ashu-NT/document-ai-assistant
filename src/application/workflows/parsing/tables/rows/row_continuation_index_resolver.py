from __future__ import annotations

from src.application.workflows.parsing.tables.rows.row_continuation_patterns import (
    resolve_sparse_continuation_indexes,
)
from src.application.workflows.parsing.tables.rows.span_aware_row_continuation_resolver import (
    SpanAwareRowContinuationResolver,
)
from src.domain.assets.table_cell_span import TableCellSpan


class RowContinuationIndexResolver:
    def __init__(
        self,
        *,
        span_aware_resolver: SpanAwareRowContinuationResolver | None = None,
    ) -> None:
        self.span_aware_resolver = (
            span_aware_resolver or SpanAwareRowContinuationResolver()
        )

    def resolve(
        self,
        previous_row: list[str],
        current_row: list[str],
        *,
        max_non_empty_cells: int | None = 3,
        previous_row_index: int | None = None,
        current_row_index: int | None = None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> list[int]:
        indexes = resolve_sparse_continuation_indexes(
            previous_row,
            current_row,
            max_non_empty_cells=max_non_empty_cells,
        )
        if indexes:
            return indexes
        if previous_row_index is None or current_row_index is None:
            return []
        return self.span_aware_resolver.resolve(
            previous_row,
            current_row,
            previous_row_index=previous_row_index,
            current_row_index=current_row_index,
            cell_spans=cell_spans,
        )
