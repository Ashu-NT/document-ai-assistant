from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.application.langgraph.research.models.research_gap import ResearchGap


@dataclass(slots=True)
class ResearchSynthesis:
    summary: str
    sections: list[dict[str, Any]] = field(default_factory=list)
    comparisons: list[dict[str, Any]] = field(default_factory=list)
    checklist_items: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[ResearchGap] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
