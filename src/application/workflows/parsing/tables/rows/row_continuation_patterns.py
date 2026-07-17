from __future__ import annotations

from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    looks_continuation_start,
    looks_incomplete_text,
    looks_terminated_text,
    merge_continuation_text,
    normalize_cell,
)


def non_empty_cell_indexes(row: list[str]) -> list[int]:
    return [index for index, value in enumerate(row) if normalize_cell(value)]


def looks_like_continuation_pair(previous_value: str, current_value: str) -> bool:
    previous = normalize_cell(previous_value)
    current = normalize_cell(current_value)
    if not previous or not current:
        return False
    if previous.casefold() == current.casefold():
        return False
    if previous.endswith("-"):
        return True
    if looks_incomplete_text(previous):
        return True
    return not looks_terminated_text(previous) and looks_continuation_start(current)


def resolve_sparse_continuation_indexes(
    previous_row: list[str],
    current_row: list[str],
    *,
    max_non_empty_cells: int | None = 3,
) -> list[int]:
    current_indexes = non_empty_cell_indexes(current_row)
    if not current_indexes:
        return []
    if max_non_empty_cells is not None and len(current_indexes) > max_non_empty_cells:
        return []

    saw_non_anchor = False
    continuation_indexes: list[int] = []
    for index in current_indexes:
        previous_value = (
            normalize_cell(previous_row[index]) if index < len(previous_row) else ""
        )
        current_value = normalize_cell(current_row[index])
        if not previous_value:
            return []
        if index == 0:
            if current_value.casefold() != previous_value.casefold():
                return []
            continue

        saw_non_anchor = True
        if current_value.casefold() == previous_value.casefold():
            continue
        if looks_like_continuation_pair(previous_value, current_value):
            continuation_indexes.append(index)
            continue
        return []

    if not saw_non_anchor or not continuation_indexes:
        return []
    return current_indexes


def merge_row_cells(
    previous_row: list[str],
    current_row: list[str],
    *,
    indexes: list[int] | None = None,
) -> list[str]:
    merged = list(previous_row)
    merge_indexes = indexes or non_empty_cell_indexes(current_row)
    for index in merge_indexes:
        value = normalize_cell(current_row[index]) if index < len(current_row) else ""
        if not value:
            continue
        existing = merged[index] if index < len(merged) else ""
        while len(merged) <= index:
            merged.append("")
        merged[index] = merge_continuation_text(existing, value)
    return merged
