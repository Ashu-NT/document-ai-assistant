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
