import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)
from src.application.guardrails.retrieval.retrieval_evidence_guardrail import (
    RetrievalEvidenceGuardrail,
)


def make_context(chunks: list, min_evidence_chunks: int = 1) -> GuardrailContext:
    return GuardrailContext(
        query_text="test query",
        retrieved_chunks=chunks,
        min_evidence_chunks=min_evidence_chunks,
    )


def test_no_evidence_returns_no_evidence_decision(sample_retrieval_query) -> None:
    guardrail = RetrievalEvidenceGuardrail()
    context = make_context(chunks=[], min_evidence_chunks=1)

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.NO_EVIDENCE
    assert result.safe_user_message is not None
    assert len(result.violations) == 1


def test_sufficient_evidence_returns_allow(sample_retrieved_chunk) -> None:
    guardrail = RetrievalEvidenceGuardrail()
    context = make_context(chunks=[sample_retrieved_chunk], min_evidence_chunks=1)

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_fewer_chunks_than_required_returns_insufficient_evidence(
    sample_retrieved_chunk,
) -> None:
    guardrail = RetrievalEvidenceGuardrail()
    context = make_context(chunks=[sample_retrieved_chunk], min_evidence_chunks=3)

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert len(result.violations) == 1


def test_policy_min_evidence_chunks_is_respected(sample_retrieved_chunk) -> None:
    policy = RetrievalGuardrailPolicy(min_evidence_chunks=2)
    guardrail = RetrievalEvidenceGuardrail(policy=policy)
    context = make_context(chunks=[sample_retrieved_chunk], min_evidence_chunks=1)

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE


def test_policy_min_evidence_overridden_by_higher_context_min(
    sample_retrieved_chunk,
) -> None:
    policy = RetrievalGuardrailPolicy(min_evidence_chunks=1)
    guardrail = RetrievalEvidenceGuardrail(policy=policy)
    context = make_context(chunks=[sample_retrieved_chunk], min_evidence_chunks=5)

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
