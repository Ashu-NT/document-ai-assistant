from __future__ import annotations

from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.normalization.key_value.key_value_continuation_row_merger import (
    KeyValueContinuationRowMerger,
)
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    clean_rows,
)
from src.domain.assets.table_cell_span import TableCellSpan

_KEY_VALUE_CONTINUATION_ROW_MERGER = KeyValueContinuationRowMerger()


def project_key_value_rows(
    rows: list[list[str]],
    *,
    row_canonicalizer: TableRowCanonicalizer,
    cell_spans: list[TableCellSpan] | None = None,
) -> NormalizedTableRows | None:
    cleaned_rows = clean_rows(rows)
    if len(cleaned_rows) < 2:
        return None
    cleaned_rows = _KEY_VALUE_CONTINUATION_ROW_MERGER.merge(
        cleaned_rows,
        cell_spans=cell_spans,
    )
    canonical_rows = row_canonicalizer.canonicalize(cleaned_rows)
    if canonical_rows == cleaned_rows:
        return None
    if len(canonical_rows) < 2 or canonical_rows[0] != ["Label", "Value"]:
        return None
    return NormalizedTableRows(headers=canonical_rows[0], rows=canonical_rows[1:])
