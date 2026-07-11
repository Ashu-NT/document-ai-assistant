from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptTableRowView:
    source_row_index: int
    cells: list[str] = field(default_factory=list)
    cells_by_header: dict[str, str] = field(default_factory=dict)
