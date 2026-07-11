from __future__ import annotations

from src.application.langgraph.research.models import ResearchGoalType, ResearchOutputType
from src.application.langgraph.research.planners.concept_extractor import (
    concept_list_text,
)


def output_type_for_goal(goal_type: ResearchGoalType) -> ResearchOutputType:
    mapping = {
        ResearchGoalType.COMPARISON: ResearchOutputType.COMPARISON,
        ResearchGoalType.SUMMARY: ResearchOutputType.SUMMARY,
        ResearchGoalType.CHECKLIST: ResearchOutputType.CHECKLIST,
        ResearchGoalType.AUDIT: ResearchOutputType.AUDIT,
        ResearchGoalType.EVIDENCE_REVIEW: ResearchOutputType.EVIDENCE_REVIEW,
        ResearchGoalType.GAP_ANALYSIS: ResearchOutputType.EVIDENCE_REVIEW,
        ResearchGoalType.REPORT: ResearchOutputType.REPORT,
        ResearchGoalType.GENERAL_RESEARCH: ResearchOutputType.REPORT,
    }
    return mapping[goal_type]


def plan_reason(goal_type: ResearchGoalType, concepts: list[str]) -> str:
    concept_text = concept_list_text(concepts)
    return {
        ResearchGoalType.COMPARISON: (
            f"The request compares {concept_text}, so the plan collects evidence "
            "for each concept plus overlap and difference support."
        ),
        ResearchGoalType.SUMMARY: (
            f"The request asks for a document-wide summary of {concept_text}."
        ),
        ResearchGoalType.CHECKLIST: (
            f"The request needs a checklist assembled from {concept_text}, safety, "
            "and prerequisite evidence."
        ),
        ResearchGoalType.AUDIT: (
            f"The request needs cross-section audit evidence for {concept_text}."
        ),
        ResearchGoalType.EVIDENCE_REVIEW: (
            f"The request needs supporting evidence and related context for {concept_text}."
        ),
        ResearchGoalType.GAP_ANALYSIS: (
            f"The request needs supporting evidence and missing-evidence detection for {concept_text}."
        ),
        ResearchGoalType.REPORT: (
            f"The request needs a structured research report about {concept_text}."
        ),
        ResearchGoalType.GENERAL_RESEARCH: (
            f"The request needs broader document research about {concept_text}."
        ),
    }[goal_type]
