from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class ResearchGoalType(StrEnum):
    COMPARISON = "comparison"
    SUMMARY = "summary"
    CHECKLIST = "checklist"
    AUDIT = "audit"
    EVIDENCE_REVIEW = "evidence_review"
    GAP_ANALYSIS = "gap_analysis"
    REPORT = "report"
    GENERAL_RESEARCH = "general_research"


class ResearchOutputType(StrEnum):
    COMPARISON = "comparison"
    SUMMARY = "summary"
    CHECKLIST = "checklist"
    AUDIT = "audit"
    EVIDENCE_REVIEW = "evidence_review"
    REPORT = "report"


@dataclass(slots=True)
class ResearchGoal:
    goal_id: str
    user_input: str
    goal_type: ResearchGoalType
    document_id: str | None
    document_title: str | None
    requires_document: bool
    requires_cross_section_reasoning: bool
    requires_multi_strategy_retrieval: bool
    expected_output_type: ResearchOutputType
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
