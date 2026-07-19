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

    def generate(self, prompt, model=None, **kwargs) -> str:
        return self._response

class _CapturingLLMService:
    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate(self, prompt, model=None, **kwargs) -> str:
        self.prompts.append(prompt)
        return self._response

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

def test_result_diagnostics_includes_a_decision_trace(
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    """PR 7 (answering_flow_weakness_remediation_plan.md): the final
    QuestionAnsweringResult.diagnostics must carry a single decision_trace
    combining the retrieval-side classification (computed by the REAL
    QuestionAnsweringRouter/RetrievalQueryAnalyzer here, not mocked) with
    the answer-side outcome from AnswerGenerationService -- not a new
    top-level AgentState field. Reuses the exact "Show me the fault code
    table" exact-tie fixture already established for PR 1's
    RetrievalQueryAnalyzer tests, so the expected retrieval-side values are
    known-good, not guessed."""
    chunk = _make_chunk()
    wf_result = _make_retrieval_result_with_chunks([chunk])
    fake_retrieval = FakeRetrievalWorkflow(result=wf_result)
    fake_gen = FakeAnswerGenerationService(
        answer_text="It could be either.",
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
    )
    workflow = make_workflow(
        fake_retrieval,
        fake_exploration_service,
        answer_generation_service=fake_gen,
    )
    request = QuestionAnsweringRequest(
        question="Show me the fault code table",
        allow_answer_generation=True,
    )

    result = workflow.run(request)

    trace = result.diagnostics["decision_trace"]
    assert trace["retrieval_intent"] == "table"
    assert trace["retrieval_intent_runner_up"] == "troubleshooting"
    assert trace["retrieval_intent_gap"] == 0
    assert (
        trace["retrieval_intent_best_score"]
        == trace["retrieval_intent_runner_up_score"]
    )
    assert trace["answer_intent"] == "maintenance_summary"
    assert trace["renderer_used"] is None
    assert trace["llm_used"] is True

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
        "Checking answer guardrails...",
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
