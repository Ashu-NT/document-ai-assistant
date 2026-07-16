from __future__ import annotations

from src.domain.assets.table_cell_span import TableCellSpan
from src.domain.assets.table_rows.key_value_row_projection import (
    project_key_value_rows,
)
from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_canonicalizer import TableRowCanonicalizer


class CertificationParticularsTableNormalizer:
    def __init__(
        self,
        *,
        row_canonicalizer: TableRowCanonicalizer | None = None,
    ) -> None:
        self.row_canonicalizer = row_canonicalizer or TableRowCanonicalizer()

    def normalize(
        self,
        rows: list[list[str]],
        *,
        table_category: str | None,
        chunk_type: str | None,
        cell_spans: list[TableCellSpan] | None = None,
    ) -> NormalizedTableRows | None:
        if (table_category or "").strip().lower() != "certification_table":
            return None
        return project_key_value_rows(rows, row_canonicalizer=self.row_canonicalizer)
