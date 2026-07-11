from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)

from src.application.langgraph.reflection.policies import ReflectionPolicy

from src.application.langgraph.reflection.validation import ReflectionValidator


def test_validator_fails_safe_when_clarify_decision_has_no_clarification_question() -> None:
    """Reproduces the exact investigation misfire (finding 4.4c): a CLARIFY
    decision with a missing clarification_question, and no maintenance/
    spare-parts/identifier downgrade context in play, used to silently fall
    through to ACCEPT_WITH_LIMITATIONS just because useful evidence existed.
    It must now fail safe instead, since the user never actually got a
    chance to clarify."""
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.CLARIFY,
            confidence=0.6,
            reason="Need clarification.",
            clarification_question=None,
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What is the pump flow rate specification?",
        answer_intent="specification",
        answer_text="The pump flow rate is 120 m3/h.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=False,
    )

    assert result.decision == ReflectionDecisionType.FAIL
    assert result.diagnostics.get("validator") == "missing_clarification_question"


def test_validator_still_fails_safe_when_clarify_has_no_question_and_no_evidence() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.CLARIFY,
            confidence=0.6,
            reason="Need clarification.",
            clarification_question="",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What is the pump flow rate specification?",
        answer_intent="specification",
        answer_text="",
        has_useful_evidence=False,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=False,
    )

    assert result.decision == ReflectionDecisionType.FAIL


def test_validator_clarify_with_real_question_is_unaffected() -> None:
    """Confirms the legitimate case (a real clarification_question present)
    still passes through as CLARIFY, unchanged by the fail-safe fix."""
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.CLARIFY,
            confidence=0.6,
            reason="Need clarification.",
            clarification_question="Do you mean the inlet or outlet flow rate?",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What is the pump flow rate specification?",
        answer_intent="specification",
        answer_text="The pump flow rate is 120 m3/h.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=False,
    )

    assert result.decision == ReflectionDecisionType.CLARIFY
    assert result.clarification_question == "Do you mean the inlet or outlet flow rate?"
