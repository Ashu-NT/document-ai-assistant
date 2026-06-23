import pytest

from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.services.document_exploration.document_exploration_result import (
    DocumentExplorationResult,
)
from src.application.services.document_exploration.document_exploration_service import (
    DocumentNotFoundError,
)
from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.application.workflows.question_answering.question_answering_workflow import (
    QuestionAnsweringWorkflow,
)
from src.application.workflows.retrieval.retrieval_query_chunk_type_preference_mapper import (
    RetrievalQueryChunkTypePreferenceMapper,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval import RetrievalQuery, RetrievalResult
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk

from tests.unit.application.workflows.question_answering.conftest import (
    FakeAnswerGenerationService,
    FakeDocumentExplorationService,
    FakeGuardrail,
    FakeRetrievalWorkflow,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_workflow(
    fake_retrieval: FakeRetrievalWorkflow,
    fake_exploration: FakeDocumentExplorationService,
    pre_query_guardrails=None,
    context_guardrails=None,
    answer_generation_service=None,
    post_answer_guardrails=None,
) -> QuestionAnsweringWorkflow:
    return QuestionAnsweringWorkflow(
        retrieval_workflow=fake_retrieval,
        exploration_service=fake_exploration,
        pre_query_guardrails=pre_query_guardrails,
        context_guardrails=context_guardrails,
        answer_generation_service=answer_generation_service,
        post_answer_guardrails=post_answer_guardrails,
    )


def _make_chunk(chunk_id: str = "chunk_001", citation: Citation | None = None) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content="Technical content.",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.GENERAL,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        citation=citation,
    )


def _make_retrieval_result_with_chunks(
    chunks: list[RetrievedChunk],
) -> RetrievalWorkflowResult:
    query = RetrievalQuery(query_id="q_test", query_text="test")
    result = RetrievalResult(result_id="r_test", query=query, chunks=chunks)
    return RetrievalWorkflowResult(
        retrieval_result=result,
        enough_evidence=True,
        min_evidence_chunks=1,
        context_chunks=chunks,
    )


# ---------------------------------------------------------------------------
# Test 1 — DOCUMENT_EXPLORATION routes to DocumentExplorationService
# ---------------------------------------------------------------------------


def test_exploration_query_calls_exploration_service(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What sections are in this document?",
        document_id="doc_001",
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION
    assert fake_exploration_service.called_with == "doc_001"
    assert result.document_exploration_result is not None


# ---------------------------------------------------------------------------
# Test 2 — DOCUMENT_EXPLORATION does NOT call RetrievalWorkflow
# ---------------------------------------------------------------------------


def test_exploration_query_bypasses_retrieval_workflow(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What information is available in this document?",
        document_id="doc_001",
    )

    workflow.run(request)

    assert fake_retrieval_workflow.called is False


# ---------------------------------------------------------------------------
# Test 3 — DOCUMENT_EXPLORATION without document_id returns safe result
# ---------------------------------------------------------------------------


def test_exploration_without_document_id_returns_safe_message(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What sections are in this document?",
        document_id=None,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION
    assert result.safe_user_message is not None
    assert result.document_exploration_result is None
    assert fake_exploration_service.called_with is None


# ---------------------------------------------------------------------------
# Test 4 — Identifier query routes to RetrievalWorkflow
# ---------------------------------------------------------------------------


def test_identifier_query_routes_to_retrieval(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is part number PN-12345?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True


# ---------------------------------------------------------------------------
# Test 5 — Specification query routes to RetrievalWorkflow
# ---------------------------------------------------------------------------


def test_specification_query_routes_to_retrieval(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the maximum voltage specification?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True


# ---------------------------------------------------------------------------
# Test 6 — Procedure query routes to RetrievalWorkflow
# ---------------------------------------------------------------------------


def test_procedure_query_routes_to_retrieval(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="How to replace the hydraulic filter?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True


# ---------------------------------------------------------------------------
# Test 7 — Guardrail-blocked query returns BLOCKED_BY_GUARDRAIL
# ---------------------------------------------------------------------------


def test_out_of_scope_guardrail_returns_blocked_route(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    guardrail = FakeGuardrail(
        allowed=False,
        decision=GuardrailDecision.OUT_OF_SCOPE,
        safe_user_message="This question is outside the scope of technical documentation.",
    )
    workflow = make_workflow(
        fake_retrieval_workflow,
        fake_exploration_service,
        pre_query_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(question="What is the weather today?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.guardrail_decision == GuardrailDecision.OUT_OF_SCOPE
    assert result.safe_user_message is not None
    assert fake_retrieval_workflow.called is False
    assert fake_exploration_service.called_with is None


# ---------------------------------------------------------------------------
# Test 8 — NEEDS_CLARIFICATION guardrail returns NEEDS_CLARIFICATION route
# ---------------------------------------------------------------------------


def test_clarification_guardrail_returns_needs_clarification_route(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    guardrail = FakeGuardrail(
        allowed=False,
        decision=GuardrailDecision.NEEDS_CLARIFICATION,
        safe_user_message="Could you clarify what you mean?",
    )
    workflow = make_workflow(
        fake_retrieval_workflow,
        fake_exploration_service,
        pre_query_guardrails=[guardrail],
    )
    request = QuestionAnsweringRequest(question="it")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.NEEDS_CLARIFICATION
    assert result.guardrail_decision == GuardrailDecision.NEEDS_CLARIFICATION


# ---------------------------------------------------------------------------
# Test 9 — Retrieval QA result includes retrieval_result
# ---------------------------------------------------------------------------


def test_retrieval_qa_result_includes_retrieval_result(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
    empty_workflow_result: RetrievalWorkflowResult,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the torque specification?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.retrieval_result is empty_workflow_result


# ---------------------------------------------------------------------------
# Test 10 — Document exploration result includes document_exploration_result
# ---------------------------------------------------------------------------


def test_exploration_result_includes_document_exploration_result(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
    sample_exploration_result: DocumentExplorationResult,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="List all sections in this document",
        document_id="doc_001",
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION
    assert result.document_exploration_result is sample_exploration_result


# ---------------------------------------------------------------------------
# Test 11 — allow_answer_generation=False yields placeholder answer_text
# ---------------------------------------------------------------------------


def test_answer_generation_disabled_returns_placeholder_message(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What is the operating pressure?",
        allow_answer_generation=False,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text is not None
    assert "not configured" in result.answer_text


# ---------------------------------------------------------------------------
# Test 12 — DOCUMENT_EXPLORATION branch in chunk type preference mapper
# ---------------------------------------------------------------------------


def test_mapper_document_exploration_intent_returns_overview_and_general() -> None:
    mapper = RetrievalQueryChunkTypePreferenceMapper()
    query = RetrievalQuery(query_id="q_test", query_text="what is in this document")

    result = mapper.map(query=query, intent=RetrievalQueryIntent.DOCUMENT_EXPLORATION)

    assert ChunkType.OVERVIEW in result
    assert ChunkType.GENERAL in result
    assert result[0] == ChunkType.OVERVIEW


# ---------------------------------------------------------------------------
# Test 13 — DocumentNotFoundError is caught and returns safe result
# ---------------------------------------------------------------------------


def test_exploration_document_not_found_returns_safe_message(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
) -> None:
    service = FakeDocumentExplorationService(raises=DocumentNotFoundError("doc_missing"))
    workflow = make_workflow(fake_retrieval_workflow, service)
    request = QuestionAnsweringRequest(
        question="What sections are in this document?",
        document_id="doc_missing",
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION
    assert result.safe_user_message is not None
    assert result.document_exploration_result is None


# ---------------------------------------------------------------------------
# Test 14 — Passing guardrail allows flow to proceed to retrieval
# ---------------------------------------------------------------------------


def test_passing_guardrail_allows_retrieval_to_proceed(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    passing_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.ALLOW,
    )
    workflow = make_workflow(
        fake_retrieval_workflow,
        fake_exploration_service,
        pre_query_guardrails=[passing_guardrail],
    )
    request = QuestionAnsweringRequest(question="What is the maintenance interval?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True


# ---------------------------------------------------------------------------
# Test 15 — diagnostics field is populated for retrieval path
# ---------------------------------------------------------------------------


def test_retrieval_result_diagnostics_includes_enough_evidence(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the installation torque?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert "enough_evidence" in result.diagnostics


# ---------------------------------------------------------------------------
# Test 16 — context guardrail blocks retrieval → BLOCKED_BY_GUARDRAIL
# ---------------------------------------------------------------------------


def test_context_guardrail_block_returns_blocked_route(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    blocking_guardrail = FakeGuardrail(
        allowed=False,
        decision=GuardrailDecision.NO_EVIDENCE,
        safe_user_message="No relevant context found.",
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        context_guardrails=[blocking_guardrail],
    )
    request = QuestionAnsweringRequest(question="What is the torque spec?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.safe_user_message is not None


# ---------------------------------------------------------------------------
# Test 17 — allow_answer_generation=True with no service → fallback message
# ---------------------------------------------------------------------------


def test_allow_generation_without_service_returns_not_configured(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    wf_result = _make_retrieval_result_with_chunks([])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    workflow = make_workflow(fake_retrieval, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text is not None
    assert "not configured" in result.answer_text


# ---------------------------------------------------------------------------
# Test 18 — answer generation returns answer_text in result
# ---------------------------------------------------------------------------


def test_answer_generation_answer_text_returned_in_result(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    fake_gen = FakeAnswerGenerationService(
        answer_text="The answer is 1000 hours.",
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the maintenance interval?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text == "The answer is 1000 hours."


# ---------------------------------------------------------------------------
# Test 19 — AnswerGenerationService only receives approved chunks
# ---------------------------------------------------------------------------


def test_answer_generation_receives_only_approved_chunks(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk_a = _make_chunk("chunk_a")
    chunk_b = _make_chunk("chunk_b")
    wf_result = _make_retrieval_result_with_chunks([chunk_a, chunk_b])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    # Context guardrail keeps only chunk_a
    filtering_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.ALLOW,
        approved_chunk_ids=["chunk_a"],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        context_guardrails=[filtering_guardrail],
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the pressure?",
        allow_answer_generation=True,
    )

    workflow.run(request)

    assert fake_gen.called_with is not None
    assert len(fake_gen.called_with.context_chunks) == 1
    assert fake_gen.called_with.context_chunks[0].chunk_id == "chunk_a"


# ---------------------------------------------------------------------------
# Test 20 — post-answer guardrail blocks → BLOCKED_BY_GUARDRAIL
# ---------------------------------------------------------------------------


def test_post_answer_guardrail_block_returns_blocked_route(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    post_guardrail = FakeGuardrail(
        allowed=False,
        decision=GuardrailDecision.UNSUPPORTED_CLAIMS,
        safe_user_message="The answer may contain ungrounded claims.",
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[post_guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.safe_user_message is not None


# ---------------------------------------------------------------------------
# Test 21 — approved and rejected chunk IDs are correct
# ---------------------------------------------------------------------------


def test_approved_and_rejected_chunk_ids_are_accurate(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk_a = _make_chunk("chunk_a")
    chunk_b = _make_chunk("chunk_b")
    chunk_c = _make_chunk("chunk_c")
    wf_result = _make_retrieval_result_with_chunks([chunk_a, chunk_b, chunk_c])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    # Context guardrail keeps chunk_a and chunk_b
    filtering_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.ALLOW,
        approved_chunk_ids=["chunk_a", "chunk_b"],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        context_guardrails=[filtering_guardrail],
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the pressure?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert set(result.approved_chunk_ids) == {"chunk_a", "chunk_b"}
    assert result.rejected_chunk_ids == ["chunk_c"]


# ---------------------------------------------------------------------------
# Test 22 — citations are returned from generated answer
# ---------------------------------------------------------------------------


def test_citations_from_generated_answer_are_in_result(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    citation = Citation(
        citation_id="cit_001",
        document_id="doc_001",
        chunk_id="chunk_001",
    )
    chunk = _make_chunk("chunk_001", citation=citation)
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    fake_gen = FakeAnswerGenerationService(
        answer_text="The filter is on page 5.",
        citations=[citation],
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="Where is the filter?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert len(result.citations) == 1
    assert result.citations[0] is citation


# ---------------------------------------------------------------------------
# Test 23 — retrieval result diagnostics include prompt_version and model_name
# ---------------------------------------------------------------------------


def test_diagnostics_include_prompt_and_model_after_generation(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the operating pressure?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert "prompt_version" in result.diagnostics
    assert "model_name" in result.diagnostics


# ---------------------------------------------------------------------------
# Test 24 — passing context guardrail does not drop chunks when no chunk IDs set
# ---------------------------------------------------------------------------


def test_pass_through_context_guardrail_preserves_all_chunks(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk_a = _make_chunk("chunk_a")
    chunk_b = _make_chunk("chunk_b")
    wf_result = _make_retrieval_result_with_chunks([chunk_a, chunk_b])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    # Guardrail allows but sets no chunk IDs (pass-through)
    pass_through = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.ALLOW,
        approved_chunk_ids=[],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        context_guardrails=[pass_through],
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What are the specs?",
        allow_answer_generation=True,
    )

    workflow.run(request)

    assert fake_gen.called_with is not None
    assert len(fake_gen.called_with.context_chunks) == 2


# ---------------------------------------------------------------------------
# Test 25 — no answer generation service, allow_answer_generation=False
# ---------------------------------------------------------------------------


def test_no_generation_service_and_disabled_returns_placeholder(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    wf_result = _make_retrieval_result_with_chunks([_make_chunk()])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    workflow = make_workflow(fake_retrieval, fake_exploration_service)
    request = QuestionAnsweringRequest(
        question="What is the operating voltage?",
        allow_answer_generation=False,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text is not None
    assert result.answer_text != ""
