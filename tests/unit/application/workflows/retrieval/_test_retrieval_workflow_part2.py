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
        self.additional_candidates_calls = []

    def retrieve(self, query) -> RetrievalResult:
        self.calls.append(query)
        return self.result

    def retrieve_with_additional_candidates(
        self,
        query,
        *,
        additional_candidates=None,
    ) -> RetrievalResult:
        self.calls.append(query)
        self.additional_candidates_calls.append(list(additional_candidates or []))
        return self.result

class FakeStructuredEvidenceResolver:
    def __init__(self, bundle) -> None:
        self.bundle = bundle
        self.calls = []

    def resolve(self, query):
        self.calls.append(query)
        return self.bundle

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
    structured_evidence_resolver=None,
) -> RetrievalWorkflow:
    return RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=RetrievalQueryValidator(),
        min_evidence_chunks=min_evidence_chunks,
        strict_evidence=strict_evidence,
        context_expander=context_expander,
        candidate_pool_top_k=candidate_pool_top_k,
        structured_evidence_resolver=structured_evidence_resolver,
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

def test_workflow_resolves_structured_evidence_and_passes_candidates_to_hybrid_service(
    sample_retrieval_query,
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    from src.application.workflows.retrieval.structured import StructuredEvidenceBundle

    structured_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_structured_001",
        document_id=sample_retrieved_chunk.document_id,
        content="Manufacturer ACME Corp",
        score=1.2,
        retrieval_source="structured",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    resolver = FakeStructuredEvidenceResolver(
        StructuredEvidenceBundle(
            chunks=[structured_chunk],
            diagnostics={"structured_chunk_count": 1},
        )
    )
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        structured_evidence_resolver=resolver,
    )

    result = workflow.run(sample_retrieval_query)

    assert resolver.calls == [sample_retrieval_query]
    assert retrieval_service.additional_candidates_calls == [[structured_chunk]]
    assert result.structured_evidence is not None
    assert result.structured_evidence.chunks == [structured_chunk]
    assert result.diagnostics["structured_chunk_count"] == 1
