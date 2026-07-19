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
from src.application.guardrails.retrieval.seed_evidence_guardrail import (
    SeedEvidenceGuardrail,
)
from src.application.validation.retrieval import RetrievalQueryValidator
from src.application.workflows.retrieval import RetrievalWorkflow
from src.domain.retrieval import RetrievalResult


class FakeHybridRetrievalService:
    def __init__(self, result: RetrievalResult) -> None:
        self.result = result
        self.calls: list = []

    def retrieve(self, query) -> RetrievalResult:
        return self.retrieve_with_additional_candidates(query)

    def retrieve_with_additional_candidates(
        self,
        query,
        *,
        additional_candidates=None,
    ) -> RetrievalResult:
        self.calls.append(query)
        return self.result


class FakeContextExpander:
    def __init__(self, chunks) -> None:
        self.chunks = chunks
        self.calls: list = []

    def expand(self, chunks, query=None):
        self.calls.append((chunks, query))
        return self.chunks


def make_workflow(
    retrieval_service: FakeHybridRetrievalService,
    *,
    pre_retrieval_guardrails=None,
    post_retrieval_guardrails=None,
    seed_guardrails=None,
    context_expander=None,
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
        seed_guardrails=seed_guardrails,
        context_expander=context_expander,
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


# -- Ordering: seed guardrails (pre-expansion) vs. final evidence guardrails
# (post-expansion) -- query-to-retrieval flow follow-up.


def test_final_evidence_guardrail_evaluates_the_post_expansion_chunk_set(
    sample_retrieval_query,
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    """Core ordering fix: raw retrieval alone is below min_evidence_chunks,
    but context expansion supplies a second chunk -- the final evidence
    guardrail must see the expanded set and ALLOW, not the stale
    pre-expansion count."""
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
    context_expander = FakeContextExpander([sample_retrieved_chunk, expanded_chunk])
    workflow = make_workflow(
        retrieval_service,
        context_expander=context_expander,
        post_retrieval_guardrails=[RetrievalEvidenceGuardrail()],
        min_evidence_chunks=2,
    )

    result = workflow.run(sample_retrieval_query)

    assert context_expander.calls, "expansion must have run"
    assert result.context_result_count == 2
    assert result.enough_evidence is True
    assert result.guardrail_result is None


def test_seed_guardrail_blocks_before_expansion_ever_runs_on_zero_evidence(
    sample_retrieval_query,
) -> None:
    """The new fail-fast: raw retrieval returned nothing, so there is no
    seed to expand from -- expansion must never even be attempted."""
    empty_result = RetrievalResult(
        result_id="empty_001",
        query=sample_retrieval_query,
        chunks=[],
        citations=[],
    )
    retrieval_service = FakeHybridRetrievalService(empty_result)
    context_expander = FakeContextExpander(chunks=[])
    workflow = make_workflow(
        retrieval_service,
        seed_guardrails=[SeedEvidenceGuardrail()],
        context_expander=context_expander,
    )

    result = workflow.run(sample_retrieval_query)

    assert context_expander.calls == [], "expansion must not run past a seed failure"
    assert result.context_chunks == []
    assert result.guardrail_result is not None
    assert result.guardrail_result.decision == GuardrailDecision.NO_EVIDENCE


def test_seed_guardrail_does_not_block_a_below_threshold_but_nonzero_seed(
    sample_retrieval_query,
    sample_retrieval_result,
    sample_retrieved_chunk,
) -> None:
    """A single chunk is a valid seed even though it's below
    min_evidence_chunks -- expansion must get a chance to supply more
    before sufficiency is judged."""
    retrieval_service = FakeHybridRetrievalService(sample_retrieval_result)
    expanded_chunk = sample_retrieved_chunk.__class__(
        chunk_id="chunk_context_002",
        document_id=sample_retrieved_chunk.document_id,
        content="Neighbor context chunk",
        score=0.5,
        retrieval_source="context_expansion",
        chunk_type=sample_retrieved_chunk.chunk_type,
        section_id=sample_retrieved_chunk.section_id,
        section_path=sample_retrieved_chunk.section_path,
        source=sample_retrieved_chunk.source,
    )
    context_expander = FakeContextExpander([sample_retrieved_chunk, expanded_chunk])
    workflow = make_workflow(
        retrieval_service,
        seed_guardrails=[SeedEvidenceGuardrail()],
        context_expander=context_expander,
        min_evidence_chunks=2,
    )

    result = workflow.run(sample_retrieval_query)

    assert context_expander.calls, "expansion must have run past the seed check"
    assert result.context_result_count == 2
    assert result.enough_evidence is True


def test_seed_guardrails_are_a_no_op_when_not_configured(
    sample_retrieval_query,
) -> None:
    """Backward compatibility: omitting seed_guardrails (every caller
    before this feature existed) must not change behavior for a
    zero-evidence result -- it proceeds exactly as before."""
    empty_result = RetrievalResult(
        result_id="empty_002",
        query=sample_retrieval_query,
        chunks=[],
        citations=[],
    )
    retrieval_service = FakeHybridRetrievalService(empty_result)
    context_expander = FakeContextExpander(chunks=[])
    workflow = make_workflow(retrieval_service, context_expander=context_expander)

    result = workflow.run(sample_retrieval_query)

    assert context_expander.calls, "expansion still runs without seed_guardrails configured"
    assert result.guardrail_result is None
