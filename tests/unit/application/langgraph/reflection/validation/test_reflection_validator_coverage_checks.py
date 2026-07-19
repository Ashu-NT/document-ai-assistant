from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.validation import ReflectionValidator
from src.application.services.answer_generation.coverage import (
    EXHAUSTIVE_LIST,
    ORDERED_PROCEDURE,
    SINGLE_FACT,
)


def _accept(answer_text: str) -> ReflectionDecision:
    return ReflectionDecision(
        decision=ReflectionDecisionType.ACCEPT,
        confidence=0.9,
        reason="Grounded.",
    )


def test_validator_downgrades_an_exhaustive_list_claim_over_truncated_evidence() -> None:
    """PR 9 (answering_flow_weakness_remediation_plan.md, W5/W6): an
    EXHAUSTIVE_LIST answer that reads as complete must not survive as a
    bare ACCEPT when the evidence behind it was truncated (PR 8's flag) --
    the model had no way to know its own view was capped."""
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept("Here is the complete list of spare parts: A00103, A00104."),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="List all spare parts.",
        answer_intent="table_summary",
        answer_text="Here is the complete list of spare parts: A00103, A00104.",
        coverage_requirement=EXHAUSTIVE_LIST,
        evidence_truncated=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.diagnostics["validator"] == "exhaustive_list_truncated"


def test_validator_does_not_downgrade_an_exhaustive_list_claim_when_not_truncated() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept("Here is the complete list of spare parts: A00103, A00104."),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="List all spare parts.",
        answer_intent="table_summary",
        answer_text="Here is the complete list of spare parts: A00103, A00104.",
        coverage_requirement=EXHAUSTIVE_LIST,
        evidence_truncated=False,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT


def test_validator_does_not_downgrade_an_exhaustive_list_answer_with_no_completeness_claim() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept("Spare parts found: A00103, A00104."),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="List all spare parts.",
        answer_intent="table_summary",
        answer_text="Spare parts found: A00103, A00104.",
        coverage_requirement=EXHAUSTIVE_LIST,
        evidence_truncated=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT


def test_validator_ignores_truncation_for_a_single_fact_coverage_requirement() -> None:
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept("Here is the complete list of specs: 6 bar."),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="What is the operating pressure?",
        answer_intent="specification_summary",
        answer_text="Here is the complete list of specs: 6 bar.",
        coverage_requirement=SINGLE_FACT,
        evidence_truncated=True,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT


def test_validator_downgrades_an_ordered_procedure_with_a_step_gap() -> None:
    answer_text = "Step 1: Shut off power. Step 3: Remove the housing."
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept(answer_text),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="How do I replace the hydraulic filter?",
        answer_intent="procedure_steps",
        answer_text=answer_text,
        coverage_requirement=ORDERED_PROCEDURE,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.diagnostics["validator"] == "ordered_procedure_step_gap"


def test_validator_does_not_downgrade_a_contiguous_ordered_procedure() -> None:
    answer_text = "Step 1: Shut off power. Step 2: Drain fluid. Step 3: Remove the housing."
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept(answer_text),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="How do I replace the hydraulic filter?",
        answer_intent="procedure_steps",
        answer_text=answer_text,
        coverage_requirement=ORDERED_PROCEDURE,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT


def test_validator_ignores_a_step_gap_outside_the_ordered_procedure_requirement() -> None:
    answer_text = "Step 1: Shut off power. Step 3: Remove the housing."
    validator = ReflectionValidator()

    result = validator.validate(
        decision=_accept(answer_text),
        policy=ReflectionPolicy(enabled=True),
        reflection_attempts=0,
        retrieval_retry_count=0,
        selected_document_id="doc_1",
        context_document_ids=["doc_1"],
        question="How do I replace the hydraulic filter?",
        answer_intent="procedure_steps",
        answer_text=answer_text,
        coverage_requirement=SINGLE_FACT,
    )

    assert result.decision == ReflectionDecisionType.ACCEPT
