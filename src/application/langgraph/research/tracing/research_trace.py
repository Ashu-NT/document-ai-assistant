from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ResearchTrace:
    research_goal: dict[str, Any] | None = None
    plan_source: str | None = None
    tasks: list[dict[str, Any]] = field(default_factory=list)
    task_tool_names: dict[str, list[str]] = field(default_factory=dict)
    retrieval_strategies_per_task: dict[str, str] = field(default_factory=dict)
    evidence_counts_per_task: dict[str, int] = field(default_factory=dict)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    followup_iteration: bool = False
    synthesis_model: str | None = None
    final_report_sections: list[str] = field(default_factory=list)
    elapsed_ms: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
