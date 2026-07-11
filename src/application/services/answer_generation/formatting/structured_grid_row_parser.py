from __future__ import annotations

import re
from typing import Sequence

from src.application.services.answer_generation.formatting.spare_parts_row_fields import (
    CONTENT_FIELDS,
    ROW_FIELD_ALIASES,
    has_identifying_content,
)

HEADER_SEPARATOR_PATTERN = re.compile(
    r"^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)+\|?$"
)


def split_cells(line: str) -> list[str]:
    stripped = line
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _normalize_cell(cell: str) -> str:
    return " ".join(cell.lower().strip(" :").split())


def _exact_field_for_cell(cell: str) -> str | None:
    for key, aliases in ROW_FIELD_ALIASES.items():
        if cell in aliases:
            return key
    return None


def as_structured_header(cells: Sequence[str]) -> list[str | None] | None:
    # Only an exact match against a known column label counts as a header
    # cell. Real-world exports frequently squeeze several column labels into
    # a single cell (e.g. "Qty: Denomination: Part No:") -- a fuzzy/substring
    # match would misread that merged cell as one clean column and corrupt
    # every row parsed underneath it.
    normalized_cells = [_normalize_cell(cell) for cell in cells]
    mapped: list[str | None] = []
    seen_fields: set[str] = set()
    content_field_found = False
    for cell in normalized_cells:
        field_key = _exact_field_for_cell(cell)
        if field_key is not None:
            if field_key in seen_fields:
                return None
            seen_fields.add(field_key)
            if field_key in CONTENT_FIELDS:
                content_field_found = True
        mapped.append(field_key)
    if len(seen_fields) < 2 or not content_field_found:
        return None
    return mapped


def row_from_structured_cells(
    cells: Sequence[str],
    header: Sequence[str | None],
) -> dict[str, str] | None:
    row: dict[str, str] = {}
    for index, field_key in enumerate(header):
        if field_key is None or index >= len(cells):
            continue
        value = cells[index].strip().strip(":").strip()
        if not value or value in {"-", "|"}:
            continue
        row[field_key] = value
    if not row or not has_identifying_content(row):
        return None
    return row


def rows_from_structured_grid(
    grid: list[list[str]] | None,
) -> tuple[list[dict[str, str]], list[str], bool, int] | None:
    """Builds rows directly from a source's already-decoded table_rows grid
    (AnswerSource.table_rows, decoded from table_rows_json metadata by
    StructuredSourceBuilder), reusing the same header-matching/cell-mapping
    logic as the markdown path in the dispatcher -- just fed already-split
    cells instead of markdown-split ones. Returns None when there's no usable
    structured grid (absent or no recognizable header row), signalling the
    caller to fall back to regex-parsing source.content instead."""
    if not grid or len(grid) < 2:
        return None

    header = as_structured_header(grid[0])
    if header is None:
        return None

    rows: list[dict[str, str]] = []
    dropped_row_count = 0
    for cells in grid[1:]:
        row = row_from_structured_cells(cells, header)
        if row is not None:
            rows.append(row)
        else:
            dropped_row_count += 1

    if not rows:
        return None

    return rows, [], dropped_row_count > 0, dropped_row_count
