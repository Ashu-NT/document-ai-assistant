from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.retrieval.seed_evidence_guardrail import (
    SeedEvidenceGuardrail,
)


def make_context(chunks: list) -> GuardrailContext:
    return GuardrailContext(query_text="test query", retrieved_chunks=chunks)


def test_no_chunks_returns_no_evidence_decision() -> None:
    guardrail = SeedEvidenceGuardrail()
    context = make_context(chunks=[])

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.NO_EVIDENCE
    assert result.safe_user_message is not None
    assert len(result.violations) == 1


def test_a_single_chunk_is_a_valid_seed(sample_retrieved_chunk) -> None:
    """Deliberately more lenient than RetrievalEvidenceGuardrail: any
    nonzero count is a valid seed, even if it's below the eventual
    min_evidence_chunks threshold -- that threshold is the final evidence
    guardrails' job, evaluated after expansion has had a chance to help."""
    guardrail = SeedEvidenceGuardrail()
    context = make_context(chunks=[sample_retrieved_chunk])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW
