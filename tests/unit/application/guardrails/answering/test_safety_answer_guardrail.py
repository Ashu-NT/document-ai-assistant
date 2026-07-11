from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.answering.safety_answer_guardrail import (
    SafetyAnswerGuardrail,
)
from src.application.guardrails.policies.safety_guardrail_policy import (
    SafetyGuardrailPolicy,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _chunk(chunk_id: str = "chunk_001") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        content="Some safety-relevant content.",
        score=0.9,
        retrieval_source="vector",
    )


def _resolved_note(note_id: str = "r1") -> dict:
    return {"note_id": note_id, "claim_text": "claim", "source_number": 1, "chunk_id": "chunk_001"}


def _unresolved_note(note_id: str = "r1") -> dict:
    return {"note_id": note_id, "claim_text": "claim", "source_number": 99, "chunk_id": None}


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = SafetyAnswerGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_intent_is_not_safety_warnings() -> None:
    guardrail = SafetyAnswerGuardrail()
    context = GuardrailContext(answer_text="Answer.", answer_intent="general")

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_disabled_by_policy() -> None:
    guardrail = SafetyAnswerGuardrail(
        SafetyGuardrailPolicy(block_ungrounded_safety_answers=False)
    )
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="safety_warnings",
        approved_chunks=[],
        reference_notes=[],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_flags_insufficient_evidence_and_missing_citation_without_blocking() -> None:
    guardrail = SafetyAnswerGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="safety_warnings",
        approved_chunks=[],
        reference_notes=[_unresolved_note()],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.SAFETY_BLOCKED
    assert len(result.violations) == 2
    fields = {violation.field for violation in result.violations}
    assert fields == {"approved_chunks", "reference_notes"}


def test_check_allows_when_evidence_and_citation_are_sufficient() -> None:
    guardrail = SafetyAnswerGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="safety_warnings",
        approved_chunks=[_chunk()],
        reference_notes=[_resolved_note()],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []
