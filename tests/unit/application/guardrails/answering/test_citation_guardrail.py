from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.answering.citation_guardrail import CitationGuardrail
from src.application.guardrails.policies.answer_guardrail_policy import (
    AnswerGuardrailPolicy,
)


def _resolved_note(note_id: str = "r1", source_number: int = 1) -> dict:
    return {
        "note_id": note_id,
        "claim_text": "claim",
        "source_number": source_number,
        "chunk_id": "chunk_001",
    }


def _unresolved_note(note_id: str = "r1", source_number: int = 99) -> dict:
    return {
        "note_id": note_id,
        "claim_text": "claim",
        "source_number": source_number,
        "chunk_id": None,
    }


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = CitationGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_require_citations_disabled_by_policy() -> None:
    guardrail = CitationGuardrail(AnswerGuardrailPolicy(require_citations=False))
    context = GuardrailContext(
        answer_text="Answer.",
        reference_notes=[_unresolved_note()],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_when_all_reference_notes_resolve() -> None:
    guardrail = CitationGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        reference_notes=[_resolved_note(), _resolved_note(note_id="r2", source_number=2)],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_with_no_reference_notes_at_all() -> None:
    guardrail = CitationGuardrail()
    context = GuardrailContext(answer_text="Answer.", reference_notes=[])

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_flags_unresolved_source_number_without_blocking() -> None:
    guardrail = CitationGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        reference_notes=[_resolved_note(), _unresolved_note(note_id="r2", source_number=99)],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.CITATION_REQUIRED
    assert len(result.violations) == 1
    violation = result.violations[0]
    assert violation.field == "reference_notes"
    assert "r2" in violation.description
    assert "99" in violation.description
