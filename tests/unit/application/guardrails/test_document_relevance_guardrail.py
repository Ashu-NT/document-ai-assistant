import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.retrieval.document_relevance_guardrail import (
    DocumentRelevanceGuardrail,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk


def make_chunk(chunk_id: str, chunk_type: ChunkType) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content="Sample evidence content for testing purposes here.",
        score=0.80,
        retrieval_source="dense",
        chunk_type=chunk_type,
    )


def make_context(
    chunk_types: list[str],
    chunks: list[RetrievedChunk],
    query_intent: str = "general",
) -> GuardrailContext:
    return GuardrailContext(
        query_text="test query",
        query_intent=query_intent,
        query_chunk_types=chunk_types,
        retrieved_chunks=chunks,
    )


def test_no_chunk_type_constraints_returns_allow(sample_retrieved_chunk) -> None:
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(chunk_types=[], chunks=[sample_retrieved_chunk])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_matching_procedure_chunks_returns_allow() -> None:
    chunk = make_chunk("c1", ChunkType.MAINTENANCE_PROCEDURE)
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(
        chunk_types=[ChunkType.MAINTENANCE_PROCEDURE.value],
        chunks=[chunk],
        query_intent="procedure",
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_weak_procedure_evidence_returns_insufficient_evidence() -> None:
    chunk = make_chunk("c1", ChunkType.GENERAL)
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(
        chunk_types=[ChunkType.MAINTENANCE_PROCEDURE.value],
        chunks=[chunk],
        query_intent="procedure",
    )

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE


def test_weak_specification_evidence_returns_insufficient_evidence() -> None:
    chunk = make_chunk("c1", ChunkType.OVERVIEW)
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(
        chunk_types=[ChunkType.TECHNICAL_SPECIFICATION.value],
        chunks=[chunk],
        query_intent="specification",
    )

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE


def test_weak_safety_evidence_returns_safety_blocked() -> None:
    chunk = make_chunk("c1", ChunkType.GENERAL)
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(
        chunk_types=[ChunkType.SAFETY_WARNING.value],
        chunks=[chunk],
        query_intent="safety",
    )

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.SAFETY_BLOCKED
    assert result.safe_user_message is not None


def test_no_chunks_with_chunk_type_constraints_returns_allow() -> None:
    guardrail = DocumentRelevanceGuardrail()
    context = make_context(
        chunk_types=[ChunkType.MAINTENANCE_PROCEDURE.value],
        chunks=[],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW
