from __future__ import annotations

from src.domain.assets.table_rows.normalized_table_rows import NormalizedTableRows
from src.domain.assets.table_rows.table_row_canonicalizer import TableRowCanonicalizer
from src.domain.assets.table_rows.table_row_patterns import clean_rows


def project_key_value_rows(
    rows: list[list[str]],
    *,
    row_canonicalizer: TableRowCanonicalizer,
) -> NormalizedTableRows | None:
    """Projects a wrapped/unlabeled key-value table into explicit
    ``Label``/``Value`` rows, reusing `TableRowCanonicalizer`'s existing
    generic (category-agnostic) key-value detection.

    Returns `None` when the canonicalizer found nothing to project (the
    rows already have an explicit header, or don't look like key-value
    pairs at all), or when it transformed the rows for a different reason
    (e.g. a compact schedule matrix) rather than into `Label`/`Value` shape.
    """
    cleaned_rows = clean_rows(rows)
    if len(cleaned_rows) < 2:
        return None
    canonical_rows = row_canonicalizer.canonicalize(cleaned_rows)
    if canonical_rows == cleaned_rows:
        return None
    if len(canonical_rows) < 2 or canonical_rows[0] != ["Label", "Value"]:
        return None
    return NormalizedTableRows(headers=canonical_rows[0], rows=canonical_rows[1:])
