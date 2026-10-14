from __future__ import annotations

from dataclasses import replace as dataclass_replace

from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.table_windowing import (
    TableEvidenceWindowBuilder,
    resolve_composed_table,
)
from src.domain.assets import TableAsset


def expand_oversized_table_batch(
    batch: ExtractionBatch,
    *,
    tables: dict[str, TableAsset],
    window_builder: TableEvidenceWindowBuilder,
) -> list[ExtractionBatch] | None:
    """Returns one ExtractionBatch per row-window when `batch` is a single
    hydrated-table chunk too large for one call, `None` when `batch` should
    be processed normally (not a table chunk, no composable table, or small
    enough to fit in one window already), or an empty list when the table
    is oversized but windows could not be safely built (caller must not
    fall back to sending the raw oversized content unbounded)."""
    if len(batch.chunks) != 1:
        return None
    chunk = batch.chunks[0]
    if not chunk.table_ids:
        return None

    composed_table = resolve_composed_table(chunk, tables)
    if composed_table is None:
        return None
    if not window_builder.should_window(composed_table):
        return None

    windows = window_builder.build_windows(composed_table, source_chunk_id=chunk.chunk_id)
    return [
        ExtractionBatch(
            batch_index=batch.batch_index,
            batch_count=batch.batch_count,
            chunks=[
                dataclass_replace(
                    chunk,
                    content=window.rendered_text,
                    table_row_start=window.row_start,
                    table_row_end=window.row_end,
                    chunk_index=window.window_index,
                    chunk_total=window.window_count,
                )
            ],
            char_count=len(window.rendered_text),
            word_count=len(window.rendered_text.split()),
        )
        for window in windows
    ]
