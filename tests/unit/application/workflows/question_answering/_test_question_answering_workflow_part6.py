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

from src.application.workflows.retrieval.query_analysis.retrieval_query_chunk_type_preference_mapper import (
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
    assert len(fake_gen.called_with.resolved_structured_entities) == 1
    # approved_chunk_ids must reflect what generation actually received,
    # including a chunk joined in after the original guardrail approval.
    assert "chunk_manufacturer" in result.approved_chunk_ids

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
    assert len(fake_gen.called_with.resolved_identifiers) == 1
