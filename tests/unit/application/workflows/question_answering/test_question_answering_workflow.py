import pytest

from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.contracts.guardrails.guardrail_violation import GuardrailViolation
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.retrieval.query_scope_guardrail import QueryScopeGuardrail
from src.application.services.answer_generation.answer_generation_result import (
    AnswerSection,
    ReferenceNote,
)
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
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
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
    FakeDocumentLookupService,
    FakeGuardrail,
    FakeRetrievalWorkflow,
    FakeStructuredEvidenceResolver,
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
    document_lookup_service=None,
    structured_evidence_resolver=None,
) -> QuestionAnsweringWorkflow:
    return QuestionAnsweringWorkflow(
        retrieval_workflow=fake_retrieval,
        exploration_service=fake_exploration,
        pre_query_guardrails=pre_query_guardrails,
        context_guardrails=context_guardrails,
        answer_generation_service=answer_generation_service,
        post_answer_guardrails=post_answer_guardrails,
        document_lookup_service=document_lookup_service,
        structured_evidence_resolver=structured_evidence_resolver,
    )


def _make_chunk(chunk_id: str = "chunk_001", citation: Citation | None = None) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=f"Technical content for {chunk_id}.",
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
    request = QuestionAnsweringRequest(
        question="What is part number PN-12345?",
        document_id="doc_001",
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True
    assert fake_retrieval_workflow.last_query is not None
    assert fake_retrieval_workflow.last_query.document_id == "doc_001"


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
    assert "not enabled" in result.answer_text


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


def test_query_scope_guardrail_allows_selected_document_follow_up_identifier_query(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(
        fake_retrieval_workflow,
        fake_exploration_service,
        pre_query_guardrails=[QueryScopeGuardrail()],
    )
    request = QuestionAnsweringRequest(
        question="list all serial and part nmubers",
        document_id="doc_001",
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True
    assert fake_retrieval_workflow.last_query is not None
    assert fake_retrieval_workflow.last_query.document_id == "doc_001"


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


def test_progress_callback_receives_stage_messages_for_full_generation_path(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService(answer_text="The answer is 1000 hours.")
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the maintenance interval?",
        allow_answer_generation=True,
    )
    messages: list[str] = []

    result = workflow.run(request, progress_callback=messages.append)

    assert result.answer_text == "The answer is 1000 hours."
    assert messages == [
        "Analyzing question...",
        "Retrieving evidence...",
        "Retrieved 1 evidence chunk(s).",
        "Checking context guardrails...",
        "Generating answer...",
        "Answer ready.",
    ]


def test_progress_callback_is_optional_and_defaults_to_no_op(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    workflow = make_workflow(fake_retrieval, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the maintenance interval?")

    # Must not raise when no progress_callback is given — the default path.
    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA


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


def test_answer_generation_refuses_wrong_document_context_for_scoped_request(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk("chunk_wrong_scope")
    chunk.document_id = "doc_other"
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the specification?",
        document_id="doc_001",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
    assert result.guardrail_decision == GuardrailDecision.INSUFFICIENT_EVIDENCE
    assert fake_gen.called_with is None


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


def test_final_result_carries_through_limitation_note_sections_and_reference_notes(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """Plan section 9.6 (sections/reference_notes redesign): these three
    GeneratedAnswer fields must reach the final QuestionAnsweringResult --
    limitation_note was previously silently dropped here, and
    sections/reference_notes are new, so both are easy to forget."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService(
        limitation_note="Only the primary interval was found.",
        sections=[AnswerSection(heading="H", body="B", reference_note_ids=["r1"])],
        reference_notes=[
            ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
        ],
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.limitation_note == "Only the primary interval was found."
    assert result.sections == [
        AnswerSection(heading="H", body="B", reference_note_ids=["r1"])
    ]
    assert result.reference_notes == [
        ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
    ]


def test_post_answer_guardrail_warnings_surface_in_diagnostics_without_blocking(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """A warn-only guardrail result (allowed=True, with violations) must
    not block the answer, but its violations must still reach
    diagnostics -- otherwise the new CitationGuardrail/UnsupportedClaim
    Guardrail checks would be computed and immediately discarded."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    warning_guardrail = FakeGuardrail(
        allowed=True,
        decision=GuardrailDecision.UNSUPPORTED_CLAIMS,
        reason="1 section(s) have no supporting reference notes.",
        violations=[
            GuardrailViolation(
                violation_type=ViolationType.UNSUPPORTED_CLAIM,
                description="Section 'H' has no reference notes supporting its content.",
                field="sections",
            )
        ],
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[warning_guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    warnings = result.diagnostics["post_answer_guardrail_warnings"]
    assert len(warnings) == 1
    assert warnings[0]["decision"] == GuardrailDecision.UNSUPPORTED_CLAIMS.value
    assert "no reference notes" in warnings[0]["violations"][0]


def test_post_answer_guardrail_context_receives_sections_and_reference_notes_as_dicts(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """GuardrailContext.sections/.reference_notes must be plain dicts, not
    the typed AnswerSection/ReferenceNote dataclasses -- matching the
    existing loose-dict convention `citations` already uses on that
    class, so guardrails/models never depends on application/services."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    spy_guardrail = FakeGuardrail(allowed=True, decision=GuardrailDecision.ALLOW)
    fake_gen = FakeAnswerGenerationService(
        sections=[AnswerSection(heading="H", body="B", reference_note_ids=["r1"])],
        reference_notes=[
            ReferenceNote(note_id="r1", claim_text="c", source_number=1, chunk_id="chunk_001")
        ],
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        post_answer_guardrails=[spy_guardrail],
    )
    request = QuestionAnsweringRequest(
        question="What is the torque spec?",
        allow_answer_generation=True,
    )

    workflow.run(request)

    received = spy_guardrail.received_contexts[0]
    assert received.sections == [
        {"heading": "H", "body": "B", "reference_note_ids": ["r1"]}
    ]
    assert received.reference_notes == [
        {"note_id": "r1", "claim_text": "c", "source_number": 1, "chunk_id": "chunk_001"}
    ]


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


def test_answer_generation_receives_retrieval_intent_and_chunk_preferences(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    chunk = _make_chunk("chunk_spec")
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService(
        answer_intent=AnswerIntent.SPECIFICATION_SUMMARY
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the pressure specification?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert fake_gen.called_with is not None
    assert fake_gen.called_with.retrieval_intent == RetrievalQueryIntent.SPECIFICATION.value
    assert fake_gen.called_with.query_intent == RetrievalQueryIntent.SPECIFICATION.value
    assert fake_gen.called_with.chunk_type_preferences
    assert fake_gen.called_with.chunk_type_preferences[0] == ChunkType.TECHNICAL_SPECIFICATION
    assert result.answer_intent == AnswerIntent.SPECIFICATION_SUMMARY


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


# ---------------------------------------------------------------------------
# Structured-fact joining — identifiers and structured entities are fetched
# and joined into the same chunk-based generation context.
# ---------------------------------------------------------------------------


def test_resolved_structured_entity_joins_missing_source_chunk_into_context(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.domain.document.entities.chunk import DocumentChunk

    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    manufacturer_source_chunk = DocumentChunk(
        chunk_id="chunk_manufacturer",
        document_id="doc_001",
        section_id=None,
        content="ACME Corp, https://acme.example, Germany",
    )
    lookup_service = FakeDocumentLookupService(
        chunks_by_id={"chunk_manufacturer": manufacturer_source_chunk}
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        document_lookup_service=lookup_service,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer website?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "name": "ACME Corp",
                "website": "https://acme.example",
                "country": "Germany",
                "source_chunk_id": "chunk_manufacturer",
                "confidence_score": 0.9,
                "_entity_type": "manufacturer",
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert lookup_service.requested_ids == ["chunk_manufacturer"]
    assert fake_gen.called_with is not None
    context_chunk_ids = {c.chunk_id for c in fake_gen.called_with.context_chunks}
    assert "chunk_a" in context_chunk_ids
    assert "chunk_manufacturer" in context_chunk_ids
    assert fake_gen.called_with.structured_context is not None
    key_value_pairs = {
        (kv.key, kv.value) for kv in fake_gen.called_with.structured_context.key_values
    }
    assert ("Manufacturer Website", "https://acme.example") in key_value_pairs
    assert ("Manufacturer Name", "ACME Corp") in key_value_pairs


def test_retrieval_workflow_structured_evidence_is_forwarded_into_generation_context(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.application.workflows.retrieval.structured import StructuredEvidenceBundle
    from src.domain.document.entities.identifier import Identifier
    from src.domain.common.enums import IdentifierType

    retrieved_chunk = _make_chunk("chunk_a")
    identifier = Identifier(
        identifier_id="identifier_001",
        document_id="doc_001",
        raw_value="HP-001",
        identifier_type=IdentifierType.PART_NUMBER,
        chunk_id="chunk_a",
        confidence_score=0.9,
    )
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    wf_result.structured_evidence = StructuredEvidenceBundle(
        identifiers=[identifier],
        structured_entities=[
            {
                "name": "ACME Corp",
                "website": "https://acme.example",
                "source_chunk_id": "chunk_a",
                "_entity_type": "manufacturer",
            }
        ],
    )
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer website and part number?",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert len(result.resolved_identifiers) == 1
    assert len(result.resolved_structured_entities) == 1
    assert fake_gen.called_with is not None
    assert len(fake_gen.called_with.resolved_identifiers) == 1
    assert len(fake_gen.called_with.resolved_structured_entities) == 1


def test_resolved_identifier_joins_missing_source_chunk_into_context(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.domain.document.entities.chunk import DocumentChunk
    from src.domain.document.entities.identifier import Identifier
    from src.domain.common.enums import IdentifierType

    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    identifier_source_chunk = DocumentChunk(
        chunk_id="chunk_identifier",
        document_id="doc_001",
        section_id=None,
        content="Part number HP-001",
    )
    lookup_service = FakeDocumentLookupService(
        chunks_by_id={"chunk_identifier": identifier_source_chunk}
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        document_lookup_service=lookup_service,
    )
    request = QuestionAnsweringRequest(
        question="What is the part number?",
        allow_answer_generation=True,
        resolved_identifiers=[
            Identifier(
                identifier_id="identifier_001",
                document_id="doc_001",
                raw_value="HP-001",
                identifier_type=IdentifierType.PART_NUMBER,
                chunk_id="chunk_identifier",
                confidence_score=0.9,
            )
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert lookup_service.requested_ids == ["chunk_identifier"]
    assert fake_gen.called_with is not None
    context_chunk_ids = {c.chunk_id for c in fake_gen.called_with.context_chunks}
    assert "chunk_identifier" in context_chunk_ids
    assert fake_gen.called_with.structured_context is not None
    key_value_pairs = {
        (kv.key, kv.value) for kv in fake_gen.called_with.structured_context.key_values
    }
    assert ("Part Number", "HP-001") in key_value_pairs


def test_resolved_structured_entity_fetches_related_contact_point_chunks(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.domain.document.entities.chunk import DocumentChunk

    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    manufacturer_source_chunk = DocumentChunk(
        chunk_id="chunk_manufacturer",
        document_id="doc_001",
        section_id=None,
        content="ACME Corp",
    )
    contact_source_chunk = DocumentChunk(
        chunk_id="chunk_contact",
        document_id="doc_001",
        section_id=None,
        content="Contact: service@acme.example",
    )
    lookup_service = FakeDocumentLookupService(
        chunks_by_id={
            "chunk_manufacturer": manufacturer_source_chunk,
            "chunk_contact": contact_source_chunk,
        }
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        document_lookup_service=lookup_service,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer email?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "name": "ACME Corp",
                "source_chunk_id": "chunk_manufacturer",
                "_entity_type": "manufacturer",
                "related_entities": [
                    {
                        "entity_type": "contact_point",
                        "entity": {
                            "contact_type": "email_address",
                            "value": "service@acme.example",
                            "owner_name": "ACME Corp",
                            "owner_entity_type": "manufacturer",
                            "source_chunk_id": "chunk_contact",
                        },
                    }
                ],
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert set(lookup_service.requested_ids) == {"chunk_manufacturer", "chunk_contact"}
    assert fake_gen.called_with is not None
    context_chunk_ids = {c.chunk_id for c in fake_gen.called_with.context_chunks}
    assert "chunk_contact" in context_chunk_ids
    key_value_pairs = {
        (kv.key, kv.value) for kv in fake_gen.called_with.structured_context.key_values
    }
    assert ("Manufacturer Email Address", "service@acme.example") in key_value_pairs


def test_answer_generation_hydrates_full_table_evidence_before_generation(
    fake_exploration_service: FakeDocumentExplorationService,
    sample_document_graph,
) -> None:
    from src.domain.document.entities.chunk import DocumentChunk

    table_chunk = next(iter(sample_document_graph.chunks.values()))
    table_chunk.content = "| HP-001 | Filter |"
    table_chunk.chunk_type = ChunkType.SPARE_PARTS_TABLE
    table_chunk.section_path = ["Spare Parts List"]
    table_chunk.table_ids = ["table_001"]
    sample_document_graph.tables["table_001"].markdown = (
        "| Part Number | Description |\n|---|---|\n| HP-001 | Filter |\n| HP-002 | Valve |"
    )

    sibling_fragment = DocumentChunk(
        chunk_id="chunk_table_002",
        document_id=table_chunk.document_id,
        section_id=table_chunk.section_id,
        content="| HP-002 | Valve |",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=list(table_chunk.section_path),
        table_ids=["table_001"],
        source=table_chunk.source,
        sequence_number=table_chunk.sequence_number + 1,
    )
    sample_document_graph.add_chunk(sibling_fragment)

    retrieved_primary = RetrievedChunk(
        chunk_id=table_chunk.chunk_id,
        document_id=table_chunk.document_id,
        content=table_chunk.content,
        score=0.95,
        retrieval_source="sql",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_id=table_chunk.section_id,
        section_path=list(table_chunk.section_path),
        source=table_chunk.source,
    )
    retrieved_sibling = RetrievedChunk(
        chunk_id=sibling_fragment.chunk_id,
        document_id=sibling_fragment.document_id,
        content=sibling_fragment.content,
        score=0.90,
        retrieval_source="sql",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_id=sibling_fragment.section_id,
        section_path=list(sibling_fragment.section_path),
        source=sibling_fragment.source,
    )
    wf_result = _make_retrieval_result_with_chunks([retrieved_primary, retrieved_sibling])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    lookup_service = FakeDocumentLookupService(
        graphs_by_document_id={"doc_001": sample_document_graph}
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        document_lookup_service=lookup_service,
    )
    request = QuestionAnsweringRequest(
        question="Show the spare parts table.",
        allow_answer_generation=True,
    )

    workflow.run(request)

    assert lookup_service.requested_document_ids == ["doc_001"]
    assert fake_gen.called_with is not None
    assert len(fake_gen.called_with.context_chunks) == 1
    assert (
        fake_gen.called_with.context_chunks[0].content
        == sample_document_graph.tables["table_001"].to_embedding_text()
    )


def test_final_evidence_preparation_deduplicates_joined_structured_source_chunks(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.domain.common.enums import IdentifierType
    from src.domain.document.entities.chunk import DocumentChunk
    from src.domain.document.entities.identifier import Identifier

    anchor_chunk = RetrievedChunk(
        chunk_id="chunk_anchor",
        document_id="doc_001",
        content="Part Number HP-001",
        score=0.95,
        retrieval_source="sql",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_id="sec_001",
        section_path=["Technical Data"],
        source=SourceLocation(page_start=1, page_end=1),
    )
    wf_result = _make_retrieval_result_with_chunks([anchor_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    identifier_source_chunk = DocumentChunk(
        chunk_id="chunk_identifier",
        document_id="doc_001",
        section_id="sec_001",
        content="Context: Part Number HP-001",
        chunk_type=ChunkType.GENERAL,
        section_path=["Technical Data"],
        source=SourceLocation(page_start=1, page_end=1),
        sequence_number=2,
    )
    lookup_service = FakeDocumentLookupService(
        chunks_by_id={"chunk_identifier": identifier_source_chunk}
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        document_lookup_service=lookup_service,
    )
    request = QuestionAnsweringRequest(
        question="What is the part number?",
        allow_answer_generation=True,
        resolved_identifiers=[
            Identifier(
                identifier_id="identifier_001",
                document_id="doc_001",
                raw_value="HP-001",
                identifier_type=IdentifierType.PART_NUMBER,
                chunk_id="chunk_identifier",
                confidence_score=0.9,
            )
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert lookup_service.requested_ids == ["chunk_identifier"]
    assert fake_gen.called_with is not None
    assert [chunk.chunk_id for chunk in fake_gen.called_with.context_chunks] == [
        "chunk_anchor"
    ]
    assert fake_gen.called_with.structured_context is not None
    key_value_pairs = {
        (kv.key, kv.value) for kv in fake_gen.called_with.structured_context.key_values
    }
    assert ("Part Number", "HP-001") in key_value_pairs


def test_resolved_maintenance_task_surfaces_linked_procedure_steps_end_to_end(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """End-to-end regression test for 4.16: a MaintenanceTask resolved with
    a task_uses_procedure-linked Procedure (complete with steps) must reach
    AnswerGenerationRequest.structured_context.structured_entities with the
    steps intact, not silently dropped the way StructuredFactKeyValueBuilder
    drops them (no "procedure" entry in its field-label map)."""
    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="How do I replace the hydraulic filter?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "task_id": "task_001",
                "title": "Replace hydraulic filter",
                "interval": "Every 500 hours",
                "source_chunk_id": "chunk_a",
                "_entity_type": "maintenance_task",
                "related_entities": [
                    {
                        "relationship_type": "task_uses_procedure",
                        "direction": "outgoing",
                        "status": "accepted",
                        "confidence_score": 0.9,
                        "entity_type": "procedure",
                        "entity_id": "procedure_001",
                        "entity": {
                            "procedure_id": "procedure_001",
                            "title": "Replace hydraulic filter",
                            "steps": [
                                "Depressurize the line.",
                                "Remove the old filter.",
                                "Install the new filter.",
                            ],
                        },
                    }
                ],
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_gen.called_with is not None
    structured_context = fake_gen.called_with.structured_context
    assert structured_context is not None
    task_entities = structured_context.entities_of_type("maintenance_task")
    assert len(task_entities) == 1
    relationships = task_entities[0].relationships
    assert len(relationships) == 1
    assert relationships[0].target_entity_type == "procedure"
    assert relationships[0].target_entity_fields["steps"] == [
        "Depressurize the line.",
        "Remove the old filter.",
        "Install the new filter.",
    ]


def test_resolved_structured_entities_without_lookup_service_do_not_crash(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """Regression test for 4.3/9.7: structured_context used to come back
    None whenever the resolved entity's source chunk couldn't be fetched
    (no lookup service here, so build_from_structured_entities() has no
    source_number to key against and produces no AnswerKeyValue rows) --
    silently discarding the organized context. It must now always be
    returned once successfully organized; the raw entity still reaches
    structured_entities via StructuredEvidenceViewBuilder, which needs the
    entity dict, not a resolved chunk."""
    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer website?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "name": "ACME Corp",
                "website": "https://acme.example",
                "source_chunk_id": "chunk_manufacturer",
                "_entity_type": "manufacturer",
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_gen.called_with is not None
    structured_context = fake_gen.called_with.structured_context
    assert structured_context is not None
    assert structured_context.key_values == []
    assert len(structured_context.structured_entities) == 1
    entity = structured_context.structured_entities[0]
    assert entity.entity_type == "manufacturer"
    assert entity.fields["name"] == "ACME Corp"
    assert len(fake_gen.called_with.context_chunks) == 1


def test_context_override_falls_back_to_structured_evidence_resolver(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    from src.application.workflows.retrieval.structured import StructuredEvidenceBundle

    override_chunk = _make_chunk("chunk_override")
    bundle = StructuredEvidenceBundle(
        structured_entities=[
            {
                "name": "ACME Corp",
                "website": "https://acme.example",
                "source_chunk_id": "chunk_override",
                "_entity_type": "manufacturer",
            }
        ]
    )
    resolver = FakeStructuredEvidenceResolver(bundle)
    fake_retrieval = FakeRetrievalWorkflow(
        result=_make_retrieval_result_with_chunks([override_chunk])
    )
    fake_gen = FakeAnswerGenerationService()
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
        structured_evidence_resolver=resolver,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer website?",
        allow_answer_generation=True,
        context_override_chunks=[override_chunk],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert resolver.calls
    assert len(result.resolved_structured_entities) == 1
    assert fake_gen.called_with is not None
    assert len(fake_gen.called_with.resolved_structured_entities) == 1


class _CountingAnswerIntentAnalyzer(AnswerIntentAnalyzer):
    def __init__(self) -> None:
        super().__init__()
        self.call_count = 0

    def analyze(self, **kwargs):
        self.call_count += 1
        return super().analyze(**kwargs)


class _StubLLMService:
    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, prompt, model=None, *, response_schema=None) -> str:
        return self._response


class _CapturingLLMService:
    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate(self, prompt, model=None, *, response_schema=None) -> str:
        self.prompts.append(prompt)
        return self._response


def test_answer_intent_is_resolved_exactly_once_when_structured_facts_are_joined(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """Regression test: AnswerIntentAnalyzer.analyze() used to run twice per
    QA turn whenever structured facts were resolved -- once in
    QuestionAnsweringWorkflow._join_structured_facts (to decide what
    AnswerContextOrganizer extracts into structured_context), and again
    inside AnswerGenerationService._resolve_request, because the workflow
    never passed its already-computed decision through. Uses a REAL
    AnswerGenerationService (not FakeAnswerGenerationService) so the fix in
    AnswerGenerationService._resolve_intent_decision is actually exercised,
    sharing one spy AnswerIntentAnalyzer instance between the workflow and
    the service to count calls across both call sites."""
    from src.domain.document.entities.chunk import DocumentChunk

    retrieved_chunk = _make_chunk("chunk_a")
    wf_result = _make_retrieval_result_with_chunks([retrieved_chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)

    manufacturer_source_chunk = DocumentChunk(
        chunk_id="chunk_manufacturer",
        document_id="doc_001",
        section_id=None,
        content="ACME Corp, Germany",
    )
    lookup_service = FakeDocumentLookupService(
        chunks_by_id={"chunk_manufacturer": manufacturer_source_chunk}
    )
    spy_analyzer = _CountingAnswerIntentAnalyzer()
    real_gen_service = AnswerGenerationService(
        llm_service=_StubLLMService(
            '{"answer_text": "ACME Corp is the manufacturer."}'
        ),
        answer_intent_analyzer=spy_analyzer,
        answer_generation_model="qwen3:8b",
    )
    workflow = QuestionAnsweringWorkflow(
        retrieval_workflow=fake_retrieval,
        exploration_service=fake_exploration_service,
        answer_generation_service=real_gen_service,
        document_lookup_service=lookup_service,
        answer_intent_analyzer=spy_analyzer,
    )
    request = QuestionAnsweringRequest(
        question="What is the manufacturer?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "name": "ACME Corp",
                "source_chunk_id": "chunk_manufacturer",
                "_entity_type": "manufacturer",
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert result.answer_text == "ACME Corp is the manufacturer."
    assert spy_analyzer.call_count == 1


def test_workflow_with_real_generation_service_preserves_relationship_graph_in_prompt(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    retrieved_chunk = _make_chunk("chunk_a")
    fake_retrieval = FakeRetrievalWorkflow(
        result=_make_retrieval_result_with_chunks([retrieved_chunk])
    )
    llm = _CapturingLLMService('{"answer_text":"Replace the hydraulic filter."}')
    real_gen_service = AnswerGenerationService(
        llm_service=llm,
        answer_generation_model="qwen3:8b",
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=real_gen_service,
    )
    request = QuestionAnsweringRequest(
        question="How do I replace the hydraulic filter?",
        allow_answer_generation=True,
        resolved_structured_entities=[
            {
                "title": "Replace hydraulic filter",
                "interval": "Every 500 hours",
                "source_chunk_id": "chunk_a",
                "_entity_type": "maintenance_task",
                "related_entities": [
                    {
                        "relationship_type": "task_uses_procedure",
                        "direction": "outgoing",
                        "status": "accepted",
                        "confidence_score": 0.9,
                        "entity_type": "procedure",
                        "entity_id": "procedure_001",
                        "entity": {
                            "procedure_id": "procedure_001",
                            "title": "Replace hydraulic filter",
                            "steps": [
                                "Depressurize the line.",
                                "Remove the old filter.",
                                "Install the new filter.",
                            ],
                        },
                    }
                ],
            }
        ],
    )

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert llm.prompts
    prompt = llm.prompts[0]
    assert '"relationship_edges": [' in prompt
    assert '"relationship_families": [' in prompt
    assert '"source_families": [' in prompt
    assert '"section_topology": [' in prompt
    assert '"relationship_type": "task_uses_procedure"' in prompt
    assert '"target_entity_type": "procedure"' in prompt


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
