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

    def generate(self, prompt, model=None, *, response_schema=None) -> str:
        return self._response

class _CapturingLLMService:
    def __init__(self, response: str) -> None:
        self._response = response
        self.prompts: list[str] = []

    def generate(self, prompt, model=None, *, response_schema=None) -> str:
        self.prompts.append(prompt)
        return self._response

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

def test_specification_query_routes_to_retrieval(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="What is the maximum voltage specification?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True

def test_procedure_query_routes_to_retrieval(
    fake_retrieval_workflow: FakeRetrievalWorkflow,
    fake_exploration_service: FakeDocumentExplorationService,
) -> None:
    workflow = make_workflow(fake_retrieval_workflow, fake_exploration_service)
    request = QuestionAnsweringRequest(question="How to replace the hydraulic filter?")

    result = workflow.run(request)

    assert result.route == QuestionAnsweringRoute.RETRIEVAL_QA
    assert fake_retrieval_workflow.called is True

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
