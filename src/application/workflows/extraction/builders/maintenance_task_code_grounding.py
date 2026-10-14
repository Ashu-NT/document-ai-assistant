from __future__ import annotations

from src.application.workflows.extraction.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.application.workflows.extraction.table_windowing import resolve_composed_table
from src.domain.assets import TableAsset
from src.domain.document import DocumentChunk

_STOPWORDS = frozenset(
    {"the", "a", "an", "of", "and", "to", "for", "as", "or", "necessary", "if"}
)


def _normalize_loose(text: str) -> str:
    words = "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
    return " ".join(word for word in words if word not in _STOPWORDS)


def _find_unique_canonical_row(
    table: TableAsset, support: TablePayloadSupport, task_code: str
) -> list[str] | None:
    cleaned_rows = support.cleaned_rows(table)
    if len(cleaned_rows) < 2:
        return None
    data_rows = cleaned_rows[1:]
    matches = [row for row in data_rows if task_code in row]
    if len(matches) != 1:
        return None
    return matches[0]


def _row_supports_title(row: list[str], title: str) -> bool:
    normalized_title = _normalize_loose(title)
    normalized_row = _normalize_loose(" ".join(row))
    if not normalized_title or not normalized_row:
        return False
    return normalized_title in normalized_row


def verify_task_code_against_canonical_row(
    *,
    task_code: str,
    title: str,
    source_chunk: DocumentChunk,
    tables: dict[str, TableAsset] | None,
    support: TablePayloadSupport | None = None,
) -> bool:
    """Conservative row-level verification: the claimed task_code must
    identify EXACTLY ONE row in the canonical table, and that SAME row's
    own cell text must support the extracted title - never a different
    (even superficially similar) row, and never based on component_name
    alone. Returns False (unverified) whenever the canonical table or a
    unique matching row can't be resolved - callers must never fall back
    to the chunk-wide existence check for the final accept/reject
    decision."""
    if not tables:
        return False
    composed_table = resolve_composed_table(source_chunk, tables)
    if composed_table is None:
        return False

    resolved_support = support or TablePayloadSupport()
    row = _find_unique_canonical_row(composed_table, resolved_support, task_code)
    if row is None:
        return False

    return _row_supports_title(row, title)
