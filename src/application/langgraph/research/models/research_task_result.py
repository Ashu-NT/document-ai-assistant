from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.application.langgraph.research.models.research_evidence import ResearchEvidence


@dataclass(slots=True)
class ResearchTaskResult:
    task_id: str
    success: bool
    tool_names: list[str] = field(default_factory=list)
    retrieval_strategy: str | None = None
    evidence: list[ResearchEvidence] = field(default_factory=list)
    answer_text: str | None = None
    errors: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
