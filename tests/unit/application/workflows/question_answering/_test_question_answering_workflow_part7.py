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
