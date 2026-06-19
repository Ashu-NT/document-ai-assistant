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
