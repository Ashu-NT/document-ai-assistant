from __future__ import annotations

from dataclasses import dataclass

# Generic, family-agnostic bounded presentation of one canonical structured
# table's rows to an LLM. Deliberately NOT MaintenanceTask-specific - any
# specialized-family extraction that operates on a large structured table
# can reuse this (see PHASE 2B MAINTENANCE TABLE ROW-WINDOW EXTRACTION
# EXPERIMENT: "BUILD THE MECHANISM GENERICALLY. VALIDATE THE POLICY
# NARROWLY.").
#
# A window is a VIEW over canonical evidence, never a replacement for it:
# `source_chunk_id` always names the real, resolvable canonical hydrated
# chunk the rows came from - it is never substituted with a synthetic
# value. `execution_window_id` is a separate, purely internal identifier
# (never shown to the model, never used as a provenance field) that lets
# retry/unresolved-work bookkeeping distinguish "this window of this
# chunk" from "this chunk as a whole".


@dataclass(slots=True, frozen=True)
class TableEvidenceWindow:
    source_chunk_id: str
    window_index: int
    window_count: int
    row_start: int
    row_end: int
    total_row_count: int
    rendered_text: str

    @property
    def execution_window_id(self) -> str:
        """Internal-only diagnostic/bookkeeping identity - never emitted to
        the model and never used in place of `source_chunk_id` for
        provenance."""
        return f"{self.source_chunk_id}::rows_{self.row_start}-{self.row_end}"
