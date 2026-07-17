from __future__ import annotations

from src.application.workflows.parsing.tables.rows.compact_schedule_matrix_canonicalizer import (
    CompactScheduleMatrixCanonicalizer,
)
from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.normalization.maintenance_schedule_continuation_row_merger import (
    MaintenanceScheduleContinuationRowMerger,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    clean_rows,
)
from src.domain.assets.table_cell_span import TableCellSpan


class MaintenanceScheduleTableNormalizer:
    def __init__(
        self,
        *,
        compact_schedule_canonicalizer: (
            CompactScheduleMatrixCanonicalizer | None
        ) = None,
        continuation_row_merger: (
            MaintenanceScheduleContinuationRowMerger | None
        ) = None,
    ) -> None:
        self.compact_schedule_canonicalizer = (
            compact_schedule_canonicalizer or CompactScheduleMatrixCanonicalizer()
        )
        self.continuation_row_merger = (
            continuation_row_merger or MaintenanceScheduleContinuationRowMerger()
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
        cleaned_rows = self.continuation_row_merger.merge(
            cleaned_rows,
            cell_spans=cell_spans,
        )
        canonical = self.compact_schedule_canonicalizer.canonicalize(cleaned_rows)
        if canonical is None or len(canonical) < 2:
            return None
        return NormalizedTableRows(headers=canonical[0], rows=canonical[1:])

    @staticmethod
    def _should_normalize(*, table_category: str | None) -> bool:
        return (table_category or "").strip().lower() == "maintenance_interval_table"
