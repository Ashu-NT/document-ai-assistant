import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.policies.retrieval_guardrail_policy import (
    RetrievalGuardrailPolicy,
)
from src.application.guardrails.retrieval.identifier_evidence_guardrail import (
    IdentifierEvidenceGuardrail,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk


def make_chunk(chunk_id: str, content: str, document_id: str = "doc_001") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        score=0.85,
        retrieval_source="dense",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
    )


def make_context(
    identifiers: list[str],
    chunks: list[RetrievedChunk],
) -> GuardrailContext:
    return GuardrailContext(
        query_text="test query",
        detected_identifiers=identifiers,
        retrieved_chunks=chunks,
    )


def test_no_identifiers_returns_allow(sample_retrieved_chunk) -> None:
    guardrail = IdentifierEvidenceGuardrail()
    context = make_context(identifiers=[], chunks=[sample_retrieved_chunk])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_identifier_found_in_chunk_returns_allow() -> None:
    chunk = make_chunk("c1", "HP-001 is the hydraulic filter part number.")
    guardrail = IdentifierEvidenceGuardrail()
    context = make_context(identifiers=["hp-001"], chunks=[chunk])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_identifier_not_found_returns_insufficient_evidence() -> None:
    chunk = make_chunk("c1", "Replace the oil filter every 500 hours.")
    guardrail = IdentifierEvidenceGuardrail()
    context = make_context(identifiers=["hp-999"], chunks=[chunk])

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert len(result.violations) == 1
    assert result.safe_user_message is not None


def test_multiple_identifiers_one_missing_returns_insufficient_evidence() -> None:
    chunk = make_chunk("c1", "HP-001 filter installed in section 3.")
    guardrail = IdentifierEvidenceGuardrail()
    context = make_context(identifiers=["hp-001", "hp-999"], chunks=[chunk])

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert any("hp-999" in v.message.lower() for v in result.violations)


def test_identifier_match_is_case_insensitive() -> None:
    chunk = make_chunk("c1", "Replace HP-001 every 1000 hours.")
    guardrail = IdentifierEvidenceGuardrail()
    context = make_context(identifiers=["HP-001"], chunks=[chunk])

    result = guardrail.check(context)

    assert result.allowed is True


def test_identifier_evidence_disabled_by_policy_returns_allow() -> None:
    policy = RetrievalGuardrailPolicy(identifier_evidence_required=False)
    guardrail = IdentifierEvidenceGuardrail(policy=policy)
    context = make_context(identifiers=["hp-999"], chunks=[])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW
