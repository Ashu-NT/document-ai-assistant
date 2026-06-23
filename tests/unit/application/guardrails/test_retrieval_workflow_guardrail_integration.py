import pytest

from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_result import GuardrailResult
from src.application.guardrails.retrieval.query_scope_guardrail import QueryScopeGuardrail
from src.application.guardrails.retrieval.retrieval_evidence_guardrail import (
    RetrievalEvidenceGuardrail,
)
from src.application.guardrails.retrieval.identifier_evidence_guardrail import (
    IdentifierEvidenceGuardrail,
)
from src.application.guardrails.retrieval.retrieval_confidence_guardrail import (
    RetrievalConfidenceGuardrail,
)
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval import RetrievalWorkflow
from src.domain.retrieval import RetrievalResult


class FakeHybridRetrievalService:
    def __init__(self, result: RetrievalResult) -> None:
        self.result = result
        self.calls: list = []

    def retrieve(self, query) -> RetrievalResult:
        self.calls.append(query)
        return self.result


def make_workflow(
    retrieval_service: FakeHybridRetrievalService,
    *,
    pre_retrieval_guardrails=None,
    post_retrieval_guardrails=None,
    min_evidence_chunks: int = 1,
    candidate_pool_top_k: int = 5,
) -> RetrievalWorkflow:
    return RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=RetrievalQueryValidator(),
        min_evidence_chunks=min_evidence_chunks,
        candidate_pool_top_k=candidate_pool_top_k,
        pre_retrieval_guardrails=pre_retrieval_guardrails,
        post_retrieval_guardrails=post_retrieval_guardrails,
    )


def test_workflow_without_guardrails_is_unchanged(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(retrieval_service)

    result = workflow.run(sample_retrieval_query)

    assert result.enough_evidence is True
    assert result.has_results() is True
    assert result.guardrail_result is None


def test_workflow_with_scope_guardrail_allows_document_query(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        pre_retrieval_guardrails=[QueryScopeGuardrail()],
    )

    result = workflow.run(sample_retrieval_query)

    assert result.enough_evidence is True
    assert result.guardrail_result is None
    assert len(retrieval_service.calls) == 1


def test_workflow_pre_guardrail_blocks_off_topic_query_without_retrieval(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    sample_retrieval_query.query_text = "What is the weather like today?"
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        pre_retrieval_guardrails=[QueryScopeGuardrail()],
    )

    result = workflow.run(sample_retrieval_query)

    assert result.allowed is False if hasattr(result, "allowed") else result.guardrail_result is not None
    assert result.guardrail_result is not None
    assert result.guardrail_result.decision == GuardrailDecision.OUT_OF_SCOPE
    assert len(retrieval_service.calls) == 0


def test_workflow_post_guardrail_attaches_result_on_pass(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        post_retrieval_guardrails=[
            RetrievalEvidenceGuardrail(),
        ],
    )

    result = workflow.run(sample_retrieval_query)

    assert result.enough_evidence is True
    assert result.guardrail_result is None


def test_workflow_post_guardrail_no_evidence_attaches_result(
    sample_retrieval_query,
) -> None:
    empty_result = RetrievalResult(
        result_id="empty_001",
        query=sample_retrieval_query,
        chunks=[],
        citations=[],
    )
    retrieval_service = FakeHybridRetrievalService(empty_result)
    workflow = make_workflow(
        retrieval_service,
        post_retrieval_guardrails=[RetrievalEvidenceGuardrail()],
    )

    result = workflow.run(sample_retrieval_query)

    assert result.enough_evidence is False
    assert result.guardrail_result is not None
    assert result.guardrail_result.decision == GuardrailDecision.NO_EVIDENCE


def test_workflow_pre_blocked_does_not_raise_strict_evidence(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    sample_retrieval_query.query_text = "Who won the football match?"
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        pre_retrieval_guardrails=[QueryScopeGuardrail()],
        min_evidence_chunks=1,
    )

    result = workflow.run(sample_retrieval_query)

    assert result.guardrail_result is not None
    assert result.guardrail_result.decision == GuardrailDecision.OUT_OF_SCOPE
    assert result.has_results() is False


def test_workflow_with_combined_guardrails_passes_end_to_end(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(
        retrieval_service,
        pre_retrieval_guardrails=[QueryScopeGuardrail()],
        post_retrieval_guardrails=[
            RetrievalEvidenceGuardrail(),
            RetrievalConfidenceGuardrail(),
        ],
    )

    result = workflow.run(sample_retrieval_query)

    assert result.enough_evidence is True
    assert result.guardrail_result is None
    assert result.has_results() is True
    assert len(retrieval_service.calls) == 1


def test_workflow_result_has_guardrail_result_field(
    sample_retrieval_query,
    sample_retrieval_result,
) -> None:
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    workflow = make_workflow(retrieval_service)

    result = workflow.run(sample_retrieval_query)

    assert hasattr(result, "guardrail_result")
    assert result.guardrail_result is None
