import pytest

from src.domain.common import ChunkType
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval import RetrievalWorkflow
from src.domain.retrieval import RetrievalResult
from src.shared.exceptions import NoEvidenceFoundError, SchemaValidationError


class FakeHybridRetrievalService:
    def __init__(self, result: RetrievalResult) -> None:
        self.result = result
        self.calls = []

    def retrieve(self, query) -> RetrievalResult:
        self.calls.append(query)
        return self.result


class FakeContextExpander:
    def __init__(self, chunks) -> None:
        self.chunks = chunks
        self.calls = []

    def expand(self, chunks, query=None):
        self.calls.append((chunks, query))
        return self.chunks


def make_workflow(
    retrieval_service: FakeHybridRetrievalService,
    *,
    min_evidence_chunks: int = 1,
    strict_evidence: bool = False,
    context_expander=None,
    candidate_pool_top_k: int = 5,
) -> RetrievalWorkflow:
    return RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=RetrievalQueryValidator(),
        min_evidence_chunks=min_evidence_chunks,
        strict_evidence=strict_evidence,
        context_expander=context_expander,
        candidate_pool_top_k=candidate_pool_top_k,
    )


def build_empty_result(sample_retrieval_query) -> RetrievalResult:
    return RetrievalResult(
        result_id="retrieval_empty_001",
        query=sample_retrieval_query,
        chunks=[],
        citations=[],
        used_dense=True,
        used_keyword=True,
        used_sql=True,
        total_candidates=0,
    )


def test_valid_query_calls_retrieval_service(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(retrieval_service)

    result = workflow.run(sample_retrieval_query)

    assert retrieval_service.calls == [sample_retrieval_query]
    assert result.retrieval_result == sample_retrieval_result
    assert result.enough_evidence is True
    assert result.result_count == 1


def test_invalid_query_raises_schema_validation_error(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(retrieval_service)
    sample_retrieval_query.query_text = "   "

    with pytest.raises(SchemaValidationError):
        workflow.run(sample_retrieval_query)

    assert retrieval_service.calls == []


def test_empty_result_returns_normally_when_strict_evidence_is_disabled(
    sample_retrieval_query,
) -> None:
    retrieval_service = FakeHybridRetrievalService(
        build_empty_result(sample_retrieval_query)
    )
    workflow = make_workflow(
        retrieval_service,
        strict_evidence=False,
    )

    result = workflow.run(sample_retrieval_query)

    assert result.has_results() is False
    assert result.enough_evidence is False
    assert result.result_count == 0


def test_empty_result_raises_when_strict_evidence_is_enabled(
    sample_retrieval_query,
) -> None:
    retrieval_service = FakeHybridRetrievalService(
        build_empty_result(sample_retrieval_query)
    )
    workflow = make_workflow(
        retrieval_service,
        strict_evidence=True,
    )

    with pytest.raises(NoEvidenceFoundError):
        workflow.run(sample_retrieval_query)


def test_not_enough_evidence_raises_when_strict_mode_requires_more_chunks(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        min_evidence_chunks=2,
        strict_evidence=True,
    )

    with pytest.raises(NoEvidenceFoundError):
        workflow.run(sample_retrieval_query)


def test_workflow_expands_context_chunks_when_expander_is_available(
    sample_retrieval_query,
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    expanded_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_context_001",
        document_id=sample_retrieved_chunk.document_id,
        content="Neighbor context chunk",
        score=0.5,
        retrieval_source="context_expansion",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    context_expander = FakeContextExpander(
        [sample_retrieved_chunk, expanded_chunk]
    )
    workflow = make_workflow(
        retrieval_service,
        context_expander=context_expander,
    )

    result = workflow.run(sample_retrieval_query)

    assert context_expander.calls == [
        (sample_retrieval_result.chunks, sample_retrieval_query)
    ]
    assert [chunk.chunk_id for chunk in result.final_chunks] == [
        sample_retrieved_chunk.chunk_id,
        "chunk_context_001",
    ]
    assert result.context_result_count == 2


def test_workflow_deduplicates_retrieval_candidates_before_final_results(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    atomic_chunk = sample_retrieved_chunk
    context_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_context_duplicate",
        document_id=sample_retrieved_chunk.document_id,
        content=f"Context: {sample_retrieved_chunk.content}",
        score=0.97,
        retrieval_source="sql_keyword",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    overview_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_overview_duplicate",
        document_id=sample_retrieved_chunk.document_id,
        content=f"Section overview: {sample_retrieved_chunk.content}",
        score=0.96,
        retrieval_source="dense",
        chunk_type=ChunkType.OVERVIEW,
        section_id="sec_parent",
        section_path=["Maintenance"],
        source=sample_retrieved_chunk.source,
    )
    unique_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_unique",
        document_id=sample_retrieved_chunk.document_id,
        content="Inspect the filter housing for leaks before restart.",
        score=0.95,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        section_id="sec_002",
        section_path=["Procedure"],
        source=sample_retrieved_chunk.source,
    )
    retrieval_result = RetrievalResult(
        result_id="retrieval_result_dedup_001",
        query=sample_retrieval_query,
        chunks=[context_chunk, overview_chunk, atomic_chunk, unique_chunk],
        citations=[],
        used_dense=True,
        used_keyword=True,
        used_sql=False,
        total_candidates=4,
    )
    retrieval_service = FakeHybridRetrievalService(retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        candidate_pool_top_k=10,
    )

    result = workflow.run(sample_retrieval_query)

    assert retrieval_service.calls[0].top_k == 10
    assert len(result.chunks) == 2
    assert {chunk.chunk_id for chunk in result.chunks} == {
        atomic_chunk.chunk_id,
        "chunk_unique",
    }


def test_workflow_preserves_document_scope_on_retrieval_results(
    sample_retrieval_query,
    sample_retrieved_chunk,
) -> None:
    sample_retrieval_query.document_id = sample_retrieved_chunk.document_id
    leaked_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_other_doc",
        document_id="doc_other",
        content="Leaked chunk content.",
        score=0.98,
        retrieval_source="dense",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    retrieval_result = RetrievalResult(
        result_id="retrieval_result_scope_001",
        query=sample_retrieval_query,
        chunks=[leaked_chunk, sample_retrieved_chunk],
        citations=[],
        used_dense=True,
        used_keyword=True,
        used_sql=True,
        total_candidates=2,
    )
    retrieval_service = FakeHybridRetrievalService(retrieval_result)
    workflow = make_workflow(retrieval_service)

    result = workflow.run(sample_retrieval_query)

    assert [chunk.document_id for chunk in result.chunks] == [
        sample_retrieved_chunk.document_id
    ]
    assert result.diagnostics["retrieval_scope_discarded_chunk_ids"] == [
        "chunk_other_doc"
    ]


def test_workflow_preserves_document_scope_on_context_expansion(
    sample_retrieval_query,
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    sample_retrieval_query.document_id = sample_retrieved_chunk.document_id
    leaked_context_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_context_other_doc",
        document_id="doc_other",
        content="Leaked context chunk.",
        score=0.5,
        retrieval_source="context_expansion",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    context_expander = FakeContextExpander(
        [sample_retrieved_chunk, leaked_context_chunk]
    )
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        context_expander=context_expander,
    )

    result = workflow.run(sample_retrieval_query)

    assert [chunk.document_id for chunk in result.final_chunks] == [
        sample_retrieved_chunk.document_id
    ]
    assert result.diagnostics["context_scope_discarded_chunk_ids"] == [
        "chunk_context_other_doc"
    ]
