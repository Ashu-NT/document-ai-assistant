from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.assets import TableCellSpan, TableParallelStream


@dataclass(slots=True)
class TableReconstructionResult:
    rows: list[list[str]]
    cell_spans: list[TableCellSpan] = field(default_factory=list)
    parallel_stream_rows: list[list[list[str]]] = field(default_factory=list)
    parallel_stream_descriptors: list[TableParallelStream] = field(default_factory=list)
    local_reading_order: str | None = None
    reconstruction_version: str | None = None

    @property
    def parallel_stream_count(self) -> int:
        return len(self.parallel_stream_rows)
