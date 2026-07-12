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
        question="Summarize the hydraulic filter maintenance context.",
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
