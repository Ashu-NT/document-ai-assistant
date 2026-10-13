from __future__ import annotations

from src.application.workflows.extraction.table_payload.table_payload_support import (
    TablePayloadSupport,
)
from src.application.workflows.parsing.tables.rows.table_row_patterns import (
    normalize_cell,
)
from src.domain.assets import TableAsset
from src.domain.extraction import MaintenanceTask

# PHASE 2B — MAINTENANCE TASK COMPONENT GROUNDING FIX.
#
# Narrow, MaintenanceTask-row-window-specific deterministic correction --
# deliberately NOT a use of TableColumnSemanticClassifier (that classifier
# has no production call sites and this task does not authorize adding
# one). This module encodes exactly one structural fact already confirmed
# by direct inspection of the real MTU source table across this
# investigation's prior diagnostics: a column whose RESOLVED header is
# literally "Item" names the equipment/component/system each row's task
# applies to. That is a narrow POLICY choice about this one family's
# evidence shape (identical in spirit to TableWindowActivationPolicy's own
# narrow `activated_entity_types` scoping), not a generic column-semantics
# mechanism.
#
# Root cause this corrects (confirmed, not assumed -- see the retained raw
# LLM response fixture `phase2b_specialized_row_window_qwen2_5_7b_calls.json`
# call index 73): the model's own JSON output already contains
# `"title": "Check engine oil level", "component_name": null` verbatim --
# the source table itself is NOT merged/ambiguous for this row (confirmed
# earlier via TableCellSpan inspection: every relevant span has row_span=1),
# so this is a genuine model-generation omission for specific rows within
# a long repeated-value run, not a parsing or table-structure defect.
#
# This function never invents a value: it only fills `component_name` when
# (a) the LLM left it null/empty, (b) the SAME canonical table that
# produced this window has a column whose resolved header is exactly
# "item" (case-insensitive), and (c) exactly one row in this window's row
# range has a cell that normalizes to the SAME text as the entity's own
# `title` -- an ambiguous or absent match is left alone, never guessed.


def _normalize_for_match(value: str | None) -> str:
    return normalize_cell(value).casefold()


def backfill_maintenance_task_component_names(
    entities: list[MaintenanceTask],
    *,
    table: TableAsset,
    row_start: int,
    row_end: int,
    support: TablePayloadSupport | None = None,
) -> int:
    """Deterministically fills `component_name` on `entities` (built from
    one MaintenanceTask row-window) from the canonical `table`'s own
    structured row data, in place. Returns how many entities were
    backfilled (for logging only -- never raises on a non-match, never
    overrides an already-populated component_name).
    """
    if not entities:
        return 0

    resolved_support = support or TablePayloadSupport()
    cleaned_rows = resolved_support.cleaned_rows(table)
    if len(cleaned_rows) < 2:
        return 0

    headers = resolved_support.resolve_headers(cleaned_rows, table.header_paths)
    item_column_index = next(
        (
            index
            for index, header in enumerate(headers)
            if header.strip().casefold() == "item"
        ),
        None,
    )
    if item_column_index is None:
        return 0

    data_rows = cleaned_rows[1:]
    window_rows = data_rows[max(row_start - 1, 0) : row_end]
    if not window_rows:
        return 0

    backfilled = 0
    for entity in entities:
        if entity.component_name:
            continue

        normalized_title = _normalize_for_match(entity.title)
        if not normalized_title:
            continue

        matching_rows = [
            row
            for row in window_rows
            if any(_normalize_for_match(cell) == normalized_title for cell in row)
        ]
        if len(matching_rows) != 1:
            continue

        row = matching_rows[0]
        if item_column_index >= len(row):
            continue

        item_value = normalize_cell(row[item_column_index])
        if not item_value:
            continue

        entity.component_name = item_value
        backfilled += 1

    return backfilled
