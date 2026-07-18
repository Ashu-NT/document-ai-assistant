from tests.unit.application.langgraph.reflection.strategies.evidence_sufficiency._evidence_sufficiency_test_helpers import (
    make_context,
    make_evidence_quality,
)

from src.application.langgraph.reflection.models import SufficiencyVerdictType
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    MaintenanceIntervalEvidenceSufficiencyStrategy,
)

_MAINTENANCE_CHUNK = {
    "document_id": "doc_1",
    "chunk_type": "maintenance_interval",
    "content": "Perform weekly maintenance every 100 operating hours.",
}


def test_maintenance_strategy_is_sufficient_for_a_grounded_interval_question() -> None:
    strategy = MaintenanceIntervalEvidenceSufficiencyStrategy()
    context = make_context(
        question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        answer_text="Weekly maintenance latest after 100 operating hours.",
        approved_chunks=[_MAINTENANCE_CHUNK],
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_maintenance_strategy_falls_back_to_generic_when_question_is_not_about_intervals() -> None:
    strategy = MaintenanceIntervalEvidenceSufficiencyStrategy()
    context = make_context(
        question="What is the operating pressure?",
        answer_intent="specification_summary",
        answer_text="The operating pressure is 6 bar.",
        approved_chunks=[_MAINTENANCE_CHUNK],
    )

    verdict = strategy.is_answer_sufficient(context)

    # Falls through to the generic strategy's own (independent) judgment --
    # here that judgment is SUFFICIENT because the generic signals are good,
    # proving this is delegation, not a hardcoded domain-only negative.
    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_maintenance_strategy_falls_back_to_generic_when_no_relevant_evidence_exists() -> None:
    strategy = MaintenanceIntervalEvidenceSufficiencyStrategy()
    context = make_context(
        question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        answer_text="No interval information found.",
        approved_chunks=[],
        evidence_quality=make_evidence_quality(has_sufficient_evidence=False),
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
