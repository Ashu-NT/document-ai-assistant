from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)

from src.application.langgraph.reflection.policies import ReflectionPolicy

from src.application.langgraph.reflection.validation import ReflectionValidator

_GROUNDED_SPARE_PARTS_ANSWER = (
    "Spare parts lists found:\n\n"
    "1. Spare Parts List\n"
    "   Pages: 85-87\n"
    "   Section: 7 Components > Vacuum / Transfer Pump\n\n"
    "   Available rows:\n"
    "   - Description: Filter\n"
    "     Part No.: A00103\n\n"
    "2. Valve List > Spare Parts\n"
    "   Pages: 97\n\n"
    "   Available rows:\n"
    "   - P&ID Position: V.00.01.01\n"
    "     Service: Dry Running Protection\n"
    "     Part No.: A00103\n\n"
    "Only partial row content was available in the retrieved context.\n"
)

def test_validator_fails_spare_parts_denial_after_retry_limit() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            confidence=0.7,
            reason="Answer is grounded but incomplete.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=1,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="table of spare part list",
        answer_intent="table_summary",
        answer_text="No spare parts list table was found.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.FAIL

def test_validator_fails_identifier_inventory_answer_without_values_after_retry_limit() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT,
            confidence=0.82,
            reason="Looks acceptable.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=1,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="list all serial numbers and part numbers",
        answer_intent="identifier_lookup",
        answer_text="The document describes pumps, valves, maintenance, and safety tasks.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
    )

    assert result.decision == ReflectionDecisionType.FAIL
