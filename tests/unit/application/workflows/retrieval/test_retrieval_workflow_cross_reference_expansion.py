from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval import RetrievalWorkflow
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval import RetrievalResult, RetrievedChunk


class FakeHybridRetrievalService:
    def __init__(self, result: RetrievalResult) -> None:
        self.result = result

    def retrieve_with_additional_candidates(self, query, *, additional_candidates=None):
        return self.result


class FakeCrossReferenceContextExpander:
    """Test double standing in for a real `CrossReferenceContextExpander`
    that resolved one inline reference to a real target chunk."""

    def __init__(self, added_chunk: RetrievedChunk) -> None:
        self.added_chunk = added_chunk
        self.calls: list[list[RetrievedChunk]] = []

    def expand(self, chunks, query=None):
        self.calls.append(list(chunks))
        return [*chunks, self.added_chunk]


def make_referenced_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_referenced_procedure",
        document_id="doc_001",
        content="Replace the injector valve as follows...",
        score=0.85,
        retrieval_source="context_expansion",
        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
        source=SourceLocation(page_start=42, page_end=42),
        metadata={"context_relation": "referenced_procedure"},
    )


def test_cross_reference_expansion_output_reaches_context_chunks(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    # Regression guard for a real design bug caught during scoping: a chunk
    # newly introduced by cross-reference expansion must appear in
    # `RetrievalWorkflowResult.context_chunks`, because that is what becomes
    # `AnswerGenerationPipeline`'s `workflow_result.final_chunks` -> the
    # input to `context_guardrail_chain.run()` -> `approved_chunks`. If this
    # expansion were wired in any later (e.g. inside
    # `FinalEvidencePreparer`, where `TableEvidenceHydrator` lives),
    # `StructuredFactJoiner.join()` would silently filter the added chunk
    # back out via its `approved_chunk_ids` check, since that set is
    # captured from `approved_chunks` before `final_evidence_preparer.
    # prepare()` ever runs -- the chunk would exist in isolated hydrator
    # tests but never reach the LLM. This test would fail if that wiring
    # mistake were reintroduced.
    referenced_chunk = make_referenced_chunk()
    cross_reference_expander = FakeCrossReferenceContextExpander(referenced_chunk)
    workflow = RetrievalWorkflow(
        retrieval_service=FakeHybridRetrievalService(sample_retrieval_result),
        query_validator=RetrievalQueryValidator(),
        cross_reference_context_expander=cross_reference_expander,
    )

    result = workflow.run(sample_retrieval_query)

    context_chunk_ids = {chunk.chunk_id for chunk in result.context_chunks}
    assert referenced_chunk.chunk_id in context_chunk_ids
    assert len(cross_reference_expander.calls) == 1


def test_no_cross_reference_expansion_when_expander_not_configured(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    workflow = RetrievalWorkflow(
        retrieval_service=FakeHybridRetrievalService(sample_retrieval_result),
        query_validator=RetrievalQueryValidator(),
        cross_reference_context_expander=None,
    )

    result = workflow.run(sample_retrieval_query)

    assert "chunk_referenced_procedure" not in {
        chunk.chunk_id for chunk in result.context_chunks
    }
