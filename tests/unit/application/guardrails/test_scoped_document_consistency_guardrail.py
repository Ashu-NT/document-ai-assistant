from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.context import ScopedDocumentConsistencyGuardrail
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(*, chunk_id: str, document_id: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        content="Structured evidence.",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_scoped_document_guardrail_allows_corpus_wide_queries() -> None:
    guardrail = ScopedDocumentConsistencyGuardrail()
    result = guardrail.check(
        GuardrailContext(
            query_text="specification",
            document_id=None,
            retrieved_chunks=[_make_chunk(chunk_id="chunk_001", document_id="doc_001")],
        )
    )

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW


def test_scoped_document_guardrail_filters_wrong_document_chunks() -> None:
    guardrail = ScopedDocumentConsistencyGuardrail()
    result = guardrail.check(
        GuardrailContext(
            query_text="specification",
            document_id="doc_001",
            retrieved_chunks=[
                _make_chunk(chunk_id="chunk_ok", document_id="doc_001"),
                _make_chunk(chunk_id="chunk_leak", document_id="doc_other"),
            ],
            approved_chunks=[
                _make_chunk(chunk_id="chunk_ok", document_id="doc_001"),
                _make_chunk(chunk_id="chunk_leak", document_id="doc_other"),
            ],
        )
    )

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW_WITH_CAUTION
    assert result.approved_chunk_ids == ["chunk_ok"]
    assert result.rejected_chunk_ids == ["chunk_leak"]


def test_scoped_document_guardrail_blocks_when_all_chunks_leak() -> None:
    guardrail = ScopedDocumentConsistencyGuardrail()
    result = guardrail.check(
        GuardrailContext(
            query_text="specification",
            document_id="doc_001",
            retrieved_chunks=[_make_chunk(chunk_id="chunk_leak", document_id="doc_other")],
        )
    )

    assert result.allowed is False
    assert result.decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
