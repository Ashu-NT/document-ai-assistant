from __future__ import annotations

from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.row_continuation_patterns import (
    merge_row_cells,
    resolve_sparse_continuation_indexes,
)
from src.domain.assets.table_rows.table_row_patterns import (
    clean_rows,
)


class GenericWrappedRowTableNormalizer:
    """Last-resort fallback: merges a "widowed" row (a row with exactly one
    populated cell, not in the first column, that continues the previous
    row's text) back into its predecessor.

    Gated on real cell-span wrap evidence from Docling (`row_span > 1` or
    multi-line `raw_lines`) rather than `table_category`, since this
    normalizer has no category concept of its own -- that evidence is
    Docling's own ground truth that some cell in this table was vertically
    split or visually wrapped, not a guess. Must run last in the
    delegation chain: it is the only normalizer that doesn't check
    `table_category` at all, so it must never claim a table a more
    specific normalizer already handled, and it must no-op when nothing
    actually needed merging.
    """

    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        if not self._has_wrap_evidence(cell_spans):
            return None

        cleaned_rows = clean_rows(rows)
        if len(cleaned_rows) < 3:
            return None

        merged_rows = self._merge_widowed_rows(cleaned_rows)
        if merged_rows == cleaned_rows:
            return None

        return NormalizedTableRows(headers=merged_rows[0], rows=merged_rows[1:])

    @staticmethod
    def _has_wrap_evidence(cell_spans: list[TableCellSpan] | None) -> bool:
        return bool(cell_spans) and any(
            span.row_span > 1 or len(span.raw_lines) > 1 for span in cell_spans
        )

    def _merge_widowed_rows(self, rows: list[list[str]]) -> list[list[str]]:
        merged: list[list[str]] = [list(rows[0])]
        for row in rows[1:]:
            if not self._should_attach(merged[-1], row):
                merged.append(list(row))
                continue
            merged[-1] = self._attach(merged[-1], row)
        return merged

    def _should_attach(self, previous_row: list[str], current_row: list[str]) -> bool:
        return bool(
            resolve_sparse_continuation_indexes(
                previous_row,
                current_row,
            )
        )

    @staticmethod
    def _attach(previous_row: list[str], current_row: list[str]) -> list[str]:
        return merge_row_cells(previous_row, current_row)
