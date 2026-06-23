import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.context.context_filtering_guardrail import (
    ContextFilteringGuardrail,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk


def make_chunk(chunk_id: str, content: str, chunk_type: ChunkType = ChunkType.GENERAL) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.85,
        retrieval_source="dense",
        chunk_type=chunk_type,
    )


def make_context(chunks: list[RetrievedChunk]) -> GuardrailContext:
    return GuardrailContext(
        query_text="maintenance procedure",
        retrieved_chunks=chunks,
    )


def test_toc_chunk_is_filtered_out() -> None:
    toc_chunk = make_chunk(
        "toc_1",
        "Table of Contents\n1. Introduction .......... 3\n2. Maintenance .......... 10\n3. Safety .......... 15",
    )
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[toc_chunk])

    result = guardrail.check(context)

    assert toc_chunk.chunk_id in result.rejected_chunk_ids
    assert any(v.violation_type == ViolationType.TOC_CHUNK for v in result.violations)


def test_atomic_evidence_chunk_is_preserved() -> None:
    evidence_chunk = make_chunk(
        "ev_1",
        "Replace hydraulic filter HP-001 every 1000 operating hours. "
        "Use only manufacturer-approved replacement parts.",
        ChunkType.MAINTENANCE_INTERVAL,
    )
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[evidence_chunk])

    result = guardrail.check(context)

    assert evidence_chunk.chunk_id in result.approved_chunk_ids
    assert evidence_chunk.chunk_id not in result.rejected_chunk_ids
    assert result.allowed is True


def test_branding_chunk_is_filtered_out() -> None:
    branding_chunk = make_chunk("brand_1", "© 2024 Acme Corp. All rights reserved.")
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[branding_chunk])

    result = guardrail.check(context)

    assert branding_chunk.chunk_id in result.rejected_chunk_ids
    assert any(v.violation_type == ViolationType.BRANDING_CHUNK for v in result.violations)


def test_noise_chunk_too_short_is_filtered_out() -> None:
    noise_chunk = make_chunk("noise_1", "Page 42")
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[noise_chunk])

    result = guardrail.check(context)

    assert noise_chunk.chunk_id in result.rejected_chunk_ids
    assert any(v.violation_type == ViolationType.NOISE_CHUNK for v in result.violations)


def test_mixed_chunks_filters_toc_preserves_evidence() -> None:
    toc_chunk = make_chunk(
        "toc_1",
        "Table of Contents\n1. Safety .......... 3\n2. Maintenance .......... 7",
    )
    evidence_chunk = make_chunk(
        "ev_1",
        "The maximum operating pressure is 250 bar. Do not exceed this limit under any circumstances.",
        ChunkType.TECHNICAL_SPECIFICATION,
    )
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[toc_chunk, evidence_chunk])

    result = guardrail.check(context)

    assert toc_chunk.chunk_id in result.rejected_chunk_ids
    assert evidence_chunk.chunk_id in result.approved_chunk_ids
    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_all_chunks_filtered_returns_insufficient_evidence() -> None:
    noise_1 = make_chunk("n1", "42")
    noise_2 = make_chunk("n2", "© 2024")
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[noise_1, noise_2])

    result = guardrail.check(context)

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert result.approved_chunk_ids == []


def test_empty_context_returns_allow() -> None:
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[])

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_safety_procedure_chunk_is_preserved() -> None:
    safety_chunk = make_chunk(
        "safety_1",
        "WARNING: Always disconnect power before performing maintenance. "
        "Failure to comply may result in serious injury or death.",
        ChunkType.SAFETY_WARNING,
    )
    guardrail = ContextFilteringGuardrail()
    context = make_context(chunks=[safety_chunk])

    result = guardrail.check(context)

    assert safety_chunk.chunk_id in result.approved_chunk_ids
    assert result.allowed is True
