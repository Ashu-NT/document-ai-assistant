from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)

# Plain strings, not a new enum hierarchy -- PR 9,
# answering_flow_weakness_remediation_plan.md deliberately keeps this a
# workflow-state-friendly string, mirroring the RetrievalQueryIntent-as-
# bare-string precedent already used across the domain/application
# boundary elsewhere in this codebase.
SINGLE_FACT = "single_fact"
BEST_EFFORT_SUMMARY = "best_effort_summary"
EXHAUSTIVE_LIST = "exhaustive_list"
ORDERED_PROCEDURE = "ordered_procedure"
COMPARISON = "comparison"

_COMPARISON_TERMS = (
    "compare",
    "difference between",
    " vs ",
    " versus ",
    "which is better",
    "pros and cons",
)
_EXHAUSTIVE_LIST_TERMS = (
    "list all",
    "list every",
    "every ",
    "all of the",
    "complete list",
    "full list",
    "how many",
    "enumerate",
)

# Any AnswerIntent not listed here (MAINTENANCE_SUMMARY, TROUBLESHOOTING,
# CERTIFICATION_SUMMARY, DOCUMENT_SUMMARY, GENERAL, and any future intent)
# defaults to BEST_EFFORT_SUMMARY below -- the least demanding requirement;
# opt-in to a stricter one only where the intent clearly warrants it.
_INTENT_COVERAGE_REQUIREMENTS: dict[AnswerIntent, str] = {
    AnswerIntent.PROCEDURE_STEPS: ORDERED_PROCEDURE,
    AnswerIntent.IDENTIFIER_LOOKUP: EXHAUSTIVE_LIST,
    AnswerIntent.TABLE_SUMMARY: EXHAUSTIVE_LIST,
    AnswerIntent.SAFETY_WARNINGS: EXHAUSTIVE_LIST,
    AnswerIntent.SPECIFICATION_SUMMARY: SINGLE_FACT,
}


def resolve_coverage_requirement(
    *,
    answer_intent: AnswerIntent | None,
    question: str | None,
) -> str:
    """What kind of completeness this answer is on the hook for --
    SINGLE_FACT / BEST_EFFORT_SUMMARY / EXHAUSTIVE_LIST / ORDERED_PROCEDURE
    / COMPARISON -- derived from the resolved answer intent plus explicit
    question wording that raises the completeness bar past what the bare
    intent implies (PR 9, answering_flow_weakness_remediation_plan.md).
    Question wording is checked first: it can only ever demand MORE
    completeness than the intent's own default, never less."""
    normalized = " ".join((question or "").strip().lower().split())
    if any(term in normalized for term in _COMPARISON_TERMS):
        return COMPARISON
    if any(term in normalized for term in _EXHAUSTIVE_LIST_TERMS):
        return EXHAUSTIVE_LIST
    return _INTENT_COVERAGE_REQUIREMENTS.get(answer_intent, BEST_EFFORT_SUMMARY)
