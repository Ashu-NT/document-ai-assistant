from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.shared.table_shape import TableShape


@dataclass(slots=True, frozen=True)
class TableStructureSummary:
    table_shape: TableShape
    quality_score: float
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)
