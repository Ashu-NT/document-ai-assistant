from __future__ import annotations

from src.application.workflows.parsing.tables.rows.normalized_table_rows import (
    NormalizedTableRows,
)
from src.application.workflows.parsing.tables.rows.table_row_canonicalizer import (
    TableRowCanonicalizer,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    clean_rows,
)


def project_key_value_rows(
    rows: list[list[str]],
    *,
    row_canonicalizer: TableRowCanonicalizer,
) -> NormalizedTableRows | None:
    cleaned_rows = clean_rows(rows)
    if len(cleaned_rows) < 2:
        return None
    canonical_rows = row_canonicalizer.canonicalize(cleaned_rows)
    if canonical_rows == cleaned_rows:
        return None
    if len(canonical_rows) < 2 or canonical_rows[0] != ["Label", "Value"]:
        return None
    return NormalizedTableRows(headers=canonical_rows[0], rows=canonical_rows[1:])
