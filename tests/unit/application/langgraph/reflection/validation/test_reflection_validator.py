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


def test_validator_retries_identifier_inventory_answer_without_identifier_values() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT,
            confidence=0.82,
            reason="Looks acceptable.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="list all serial numbers and part numbers",
        answer_intent="identifier_lookup",
        answer_text="The document describes pumps, valves, maintenance, and safety tasks.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
    )

    assert result.decision == ReflectionDecisionType.RETRIEVE_AGAIN


def test_validator_does_not_treat_spare_parts_list_question_as_identifier_inventory() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT,
            confidence=0.82,
            reason="Looks acceptable.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="spare parts list",
        answer_intent="table_summary",
        answer_text="Spare parts lists found: 1. Spare Parts List, pages 45-46.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT


def test_validator_rejects_answer_with_only_header_or_unit_artifact_rows() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            confidence=0.7,
            reason="Answer is grounded but incomplete.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="table of spare part list",
        answer_intent="table_summary",
        answer_text=(
            "Spare parts lists found:\n\n"
            "1. Spare Parts List\n"
            "   Pages: 85-87\n\n"
            "   Available rows:\n"
            "   - Quantity: Pce\n"
        ),
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.RETRIEVE_AGAIN


def test_validator_accepts_spare_parts_answer_with_real_rows_alongside_quantity() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            confidence=0.7,
            reason="Answer is grounded but incomplete.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="table of spare part list",
        answer_intent="table_summary",
        answer_text=(
            "Spare parts lists found:\n\n"
            "1. Spare Parts List\n"
            "   Pages: 85-87\n\n"
            "   Available rows:\n"
            "   - Quantity: Pce\n"
            "     Denomination: Filter\n"
            "     Spare Part No.: A00103\n"
        ),
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS


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


def test_validator_downgrades_incomplete_retrieve_again_for_grounded_spare_parts_answer() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.75,
            reason="The answer appears incomplete for the current evidence set.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="spare parts list",
        answer_intent="table_summary",
        answer_text=_GROUNDED_SPARE_PARTS_ANSWER,
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS


def test_validator_downgrades_fail_for_grounded_spare_parts_answer() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=0.9,
            reason="Reflection retry limit has already been reached.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=1,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="spare parts list",
        answer_intent="table_summary",
        answer_text=_GROUNDED_SPARE_PARTS_ANSWER,
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS


def test_validator_still_retries_when_spare_parts_answer_lacks_grounding() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.75,
            reason="The answer appears incomplete for the current evidence set.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="spare parts list",
        answer_intent="table_summary",
        answer_text="Spare parts are covered somewhere in this document.",
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.RETRIEVE_AGAIN


def test_validator_rejects_answer_that_denies_spare_parts_list_when_evidence_exists() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            confidence=0.7,
            reason="Answer is grounded but incomplete.",
        ),
        policy=ReflectionPolicy(enabled=True, max_retrieval_retries=1),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="table of spare part list",
        answer_intent="table_summary",
        answer_text=(
            "No specific spare part list table was found directly related to "
            "the question in the provided sources."
        ),
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert "serial number part number identifier list" not in (result.retry_query or "")


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
