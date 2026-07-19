from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
    SufficiencyVerdict,
    SufficiencyVerdictType,
)

from src.application.langgraph.reflection.policies import ReflectionPolicy

from src.application.langgraph.reflection.validation import ReflectionValidator

_GROUNDED_SPARE_PARTS_ANSWER = (
    "Spare parts lists found:\n\n"
    "1. Spare Parts List\n"
    "   Pages: 85-87\n"
    "   Section: 7 Components > Vacuum / Transfer Pump\n\n"
    "   Available rows:\n"
    "   +-------------+----------+\n"
    "   | Description | Part No. |\n"
    "   +-------------+----------+\n"
    "   | Filter      | A00103   |\n"
    "   +-------------+----------+\n\n"
    "2. Valve List > Spare Parts\n"
    "   Pages: 97\n\n"
    "   Available rows:\n"
    "   +----------------+------------------------+----------+\n"
    "   | P&ID Position  | Service                | Part No. |\n"
    "   +----------------+------------------------+----------+\n"
    "   | V.00.01.01     | Dry Running Protection | A00103   |\n"
    "   +----------------+------------------------+----------+\n\n"
    "Only partial row content was available in the retrieved context.\n"
)

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

def test_validator_does_not_downgrade_maintenance_clarify_when_a_hard_grounding_violation_is_flagged() -> None:
    # Regression guard: this is the fix for the confirmed P0 -- a real hard
    # grounding violation (now reachable from an LLM decision via
    # ReflectionJsonParser populating diagnostics["hard_grounding_violation"])
    # must block the maintenance-interval downgrade instead of being
    # silently overridden to ACCEPT_WITH_LIMITATIONS.
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.CLARIFY,
            confidence=0.7,
            reason="The answer contradicts the retrieved evidence.",
            clarification_question="Do you mean the daily or the weekly interval?",
            diagnostics={"hard_grounding_violation": "llm_reported_grounding_violation"},
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

    assert result.decision == ReflectionDecisionType.CLARIFY
    assert result.clarification_question == "Do you mean the daily or the weekly interval?"

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
            "   +----------+\n"
            "   | Quantity |\n"
            "   +----------+\n"
            "   | Pce      |\n"
            "   +----------+\n"
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
            "   +----------+-------------+----------------+\n"
            "   | Quantity | Description | Spare Part No. |\n"
            "   +----------+-------------+----------------+\n"
            "   | Pce      | Filter      | A00103         |\n"
            "   +----------+-------------+----------------+\n"
        ),
        has_useful_evidence=True,
        has_relevant_maintenance_evidence=False,
        has_relevant_spare_parts_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS

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


# --- generic_sufficiency_verdict -- Phase 1 of the adaptive reflection redesign ---
#
# outputs/architecture/adaptive_reflection_agentic_design_plan.md section 3.1:
# a troubleshooting/safety/procedure/etc. question (none of the 3 hardcoded
# domain contexts) previously had NO equivalent "don't discard a legitimate
# partial answer" protection at all -- it silently fell through to whatever
# the decider/LLM decided, with no fallback leniency. These tests prove the
# new additive generic_context_applies gate closes that gap without
# affecting any domain-context case (see the last test in this group).

def test_validator_downgrades_fail_for_a_non_domain_question_when_generic_sufficiency_is_sufficient() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=0.6,
            reason="Evidence seemed thin.",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What should I do if the pump alarm triggers?",
        answer_intent="troubleshooting",
        answer_text="Stop the pump and check the alarm log for the fault code.",
        has_useful_evidence=True,
        generic_sufficiency_verdict=SufficiencyVerdict(
            verdict=SufficiencyVerdictType.SUFFICIENT,
            reason="Grounded, non-duplicated, correctly-referenced answer.",
        ),
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.diagnostics.get("validator") == "fail_downgraded"


def test_validator_does_not_downgrade_a_non_domain_fail_without_a_generic_verdict() -> None:
    # Backward-compatibility guard: generic_sufficiency_verdict defaults to
    # None, so every existing caller that doesn't pass it gets identical
    # behavior to before this feature existed.
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=0.6,
            reason="Evidence seemed thin.",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What should I do if the pump alarm triggers?",
        answer_intent="troubleshooting",
        answer_text="Stop the pump and check the alarm log for the fault code.",
        has_useful_evidence=True,
    )

    assert result.decision == ReflectionDecisionType.FAIL


def test_validator_does_not_downgrade_a_non_domain_fail_when_generic_verdict_is_insufficient() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=0.6,
            reason="Evidence seemed thin.",
        ),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What should I do if the pump alarm triggers?",
        answer_intent="troubleshooting",
        answer_text="Stop the pump and check the alarm log for the fault code.",
        has_useful_evidence=True,
        generic_sufficiency_verdict=SufficiencyVerdict(
            verdict=SufficiencyVerdictType.INSUFFICIENT_RETRY,
            reason="Not enough grounded information yet.",
        ),
    )

    assert result.decision == ReflectionDecisionType.FAIL


def test_validator_maintenance_downgrade_is_unaffected_by_an_insufficient_generic_verdict() -> None:
    # The `or` composition must not require the generic verdict to also be
    # sufficient when a real domain context already matched -- domain
    # matches are independent of (and take priority over) the generic path.
    validator = ReflectionValidator()

    result = validator.validate(
        decision=ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=0.6,
            reason="Evidence seemed thin.",
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
        generic_sufficiency_verdict=SufficiencyVerdict(
            verdict=SufficiencyVerdictType.INSUFFICIENT_RETRY,
            reason="irrelevant to this case",
        ),
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.diagnostics.get("validator") == "fail_downgraded"
