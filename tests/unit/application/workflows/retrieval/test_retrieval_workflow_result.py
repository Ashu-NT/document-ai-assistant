from src.application.workflows.retrieval import RetrievalWorkflowResult


def test_retrieval_workflow_result_exposes_retrieval_result_properties(
    sample_retrieval_result,
) -> None:
    workflow_result = RetrievalWorkflowResult(
        retrieval_result=sample_retrieval_result,
        enough_evidence=True,
        min_evidence_chunks=1,
    )

    assert workflow_result.query == sample_retrieval_result.query
    assert workflow_result.result_count == 1
    assert workflow_result.chunks == sample_retrieval_result.chunks
    assert workflow_result.has_results() is True
    assert workflow_result.enough_evidence is True
    assert workflow_result.min_evidence_chunks == 1


def test_retrieval_workflow_result_prefers_context_chunks_when_available(
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    context_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_context_001",
        document_id=sample_retrieved_chunk.document_id,
        content="Context chunk",
        score=0.4,
        retrieval_source="context_expansion",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    workflow_result = RetrievalWorkflowResult(
        retrieval_result=sample_retrieval_result,
        enough_evidence=True,
        min_evidence_chunks=1,
        context_chunks=[sample_retrieved_chunk, context_chunk],
    )

    assert workflow_result.final_chunks[1].chunk_id == "chunk_context_001"
    assert workflow_result.context_result_count == 2
