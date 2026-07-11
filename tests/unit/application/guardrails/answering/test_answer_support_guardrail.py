from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.answering.answer_support_guardrail import (
    AnswerSupportGuardrail,
)
from src.application.guardrails.policies.answer_guardrail_policy import (
    AnswerGuardrailPolicy,
)


def _resolved_note(note_id: str = "r1") -> dict:
    return {"note_id": note_id, "claim_text": "claim", "source_number": 1, "chunk_id": "chunk_001"}


def _unresolved_note(note_id: str = "r1") -> dict:
    return {"note_id": note_id, "claim_text": "claim", "source_number": 99, "chunk_id": None}


def _section(heading: str, reference_note_ids: list[str]) -> dict:
    return {"heading": heading, "body": "Body text.", "reference_note_ids": reference_note_ids}


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = AnswerSupportGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_with_no_structured_breakdown_to_score() -> None:
    guardrail = AnswerSupportGuardrail()
    context = GuardrailContext(answer_text="Answer.", sections=[], reference_notes=[])

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_scores_sections_and_allows_when_all_supported() -> None:
    guardrail = AnswerSupportGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[_section("A", ["r1"]), _section("B", ["r1"])],
        reference_notes=[_resolved_note("r1")],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.diagnostics["support_score"] == 1.0


def test_check_falls_back_to_reference_notes_when_no_sections() -> None:
    guardrail = AnswerSupportGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[],
        reference_notes=[_resolved_note("r1"), _unresolved_note("r2")],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.diagnostics["support_score"] == 0.5


def test_check_flags_low_support_score_without_blocking() -> None:
    guardrail = AnswerSupportGuardrail(AnswerGuardrailPolicy(min_claim_support_score=0.9))
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[_section("A", ["r1"]), _section("B", [])],
        reference_notes=[_resolved_note("r1")],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert len(result.violations) == 1
    assert result.violations[0].field == "sections"
    assert result.diagnostics["support_score"] == 0.5
