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

def test_mapper_document_exploration_intent_returns_overview_and_general() -> None:
    mapper = RetrievalQueryChunkTypePreferenceMapper()
    query = RetrievalQuery(query_id="q_test", query_text="what is in this document")

    result = mapper.map(query=query, intent=RetrievalQueryIntent.DOCUMENT_EXPLORATION)

    assert ChunkType.OVERVIEW in result
    assert ChunkType.GENERAL in result
    assert result[0] == ChunkType.OVERVIEW

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

def test_retrieval_result_diagnostics_includes_enough_evidence(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the installation torque?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert "enough_evidence" in result.diagnostics

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
