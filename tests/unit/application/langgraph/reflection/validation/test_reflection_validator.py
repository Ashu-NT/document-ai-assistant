from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.validation import ReflectionValidator


def test_validator_downgrades_maintenance_clarify_without_question() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.CLARIFY,
            confidence=0.7,
            reason="Need clarification.",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        answer_text="Weekly maintenance latest after 100 operating hours.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS


def test_validator_retry_limit_with_maintenance_evidence_downgrades_to_accept_with_limitations() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.7,
            reason="Need more interval evidence.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=1,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        answer_text="Weekly maintenance latest after 100 operating hours.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
