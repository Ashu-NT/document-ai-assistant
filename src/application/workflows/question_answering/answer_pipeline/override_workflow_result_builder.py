from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieval_result import RetrievalResult


def build_override_workflow_result(
    *,
    request: QuestionAnsweringRequest,
    analyzed_query: RetrievalQuery,
) -> RetrievalWorkflowResult:
    """Builds a `RetrievalWorkflowResult` shape for the "override"/
    pre-resolved-chunks path, where the caller already supplied the exact
    chunks to answer from (`request.context_override_chunks`) instead of
    going through normal retrieval."""
    override_chunks = list(request.context_override_chunks or [])
    citations = [
        chunk.citation
        for chunk in override_chunks
        if isinstance(chunk.citation, Citation)
    ]
    retrieval_result = RetrievalResult(
        result_id=new_id("rr"),
        query=analyzed_query,
        chunks=override_chunks,
        citations=citations,
        total_candidates=len(override_chunks),
    )
    diagnostics: dict[str, object] = {
        "context_override_used": True,
    }
    if request.retry_query:
        diagnostics["retry_query"] = request.retry_query
    return RetrievalWorkflowResult(
        retrieval_result=retrieval_result,
        enough_evidence=retrieval_result.has_enough_evidence(1),
        min_evidence_chunks=1,
        context_chunks=override_chunks,
        diagnostics=diagnostics,
    )
