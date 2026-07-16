from __future__ import annotations

from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.compact_schedule_matrix_canonicalizer import (
    CompactScheduleMatrixCanonicalizer,
)
from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_patterns import clean_rows


class MaintenanceScheduleTableNormalizer:
    def __init__(
        self,
        *,
        compact_schedule_canonicalizer: (
            CompactScheduleMatrixCanonicalizer | None
        ) = None,
    ) -> None:
        self.compact_schedule_canonicalizer = (
            compact_schedule_canonicalizer or CompactScheduleMatrixCanonicalizer()
        )

    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        if not self._should_normalize(table_category=table_category):
            return None

        cleaned_rows = clean_rows(rows)
        canonical = self.compact_schedule_canonicalizer.canonicalize(cleaned_rows)
        if canonical is None or len(canonical) < 2:
            return None
        return NormalizedTableRows(headers=canonical[0], rows=canonical[1:])

    @staticmethod
    def _should_normalize(*, table_category: str | None) -> bool:
        return (table_category or "").strip().lower() == "maintenance_interval_table"
