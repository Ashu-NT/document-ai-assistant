import pytest

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


def make_workflow(
    retrieval_service: FakeHybridRetrievalService,
    *,
    min_evidence_chunks: int = 1,
    strict_evidence: bool = False,
) -> RetrievalWorkflow:
    return RetrievalWorkflow(
        retrieval_service=retrieval_service,
        query_validator=RetrievalQueryValidator(),
        min_evidence_chunks=min_evidence_chunks,
        strict_evidence=strict_evidence,
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
