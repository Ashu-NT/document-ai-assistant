from __future__ import annotations

from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.application.workflows.parsing.tables.normalization.key_value_row_projection import (
    project_key_value_rows,
)
from src.domain.assets.table_cell_span import TableCellSpan

_APPLICABLE_CATEGORIES = frozenset(
    {
        "technical_data_table",
        "operating_limits_table",
        "sensor_instrument_table",
        "identifier_table",
        "connection_table",
    }
)


class SpecificationKeyValueTableNormalizer:
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
        if (table_category or "").strip().lower() not in _APPLICABLE_CATEGORIES:
            return None
        return project_key_value_rows(
            rows,
            row_canonicalizer=self.row_canonicalizer,
            cell_spans=cell_spans,
        )
