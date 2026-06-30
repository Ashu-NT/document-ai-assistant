from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.application.langgraph.research.models.research_evidence import ResearchEvidence
from src.application.langgraph.research.models.research_gap import ResearchGap
from src.application.langgraph.research.models.research_plan import ResearchPlan
from src.application.langgraph.research.models.research_report import ResearchReport
from src.application.langgraph.research.models.research_synthesis import ResearchSynthesis
from src.application.langgraph.research.models.research_task_result import (
    ResearchTaskResult,
)


@dataclass(slots=True)
class ResearchResult:
    success: bool
    goal: Any
    plan: ResearchPlan
    task_results: list[ResearchTaskResult] = field(default_factory=list)
    evidence: list[ResearchEvidence] = field(default_factory=list)
    synthesis: ResearchSynthesis | None = None
    report: ResearchReport | None = None
    gaps: list[ResearchGap] = field(default_factory=list)
    iterations: int = 0
    errors: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
