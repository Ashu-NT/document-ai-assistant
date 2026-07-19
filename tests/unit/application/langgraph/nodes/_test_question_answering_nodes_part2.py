from dataclasses import dataclass, field

from src.application.langgraph.factories import ToolRegistry

from src.application.langgraph.nodes.question_answering import (
    AnswerQuestionNode,
    ExploreDocumentNode,
    RetrieveEvidenceNode,
    RetryRetrievalNode,
)

from src.application.langgraph.retrieval_strategy import (
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)

from src.application.langgraph.state import build_agent_state

from src.application.tools.common import ToolResult

from src.domain.common import ChunkType, IdentifierType, SourceLocation

from src.domain.document.entities.identifier import Identifier

from src.domain.retrieval import RetrievedChunk

class FakeQAResult:
    answer_text: str | None = None
    safe_user_message: str | None = None
    retrieval_result: object | None = None
    resolved_identifiers: list = field(default_factory=list)
    resolved_structured_entities: list = field(default_factory=list)

class FakeExplorationResult:
    overview: object
    sections: list[object] = field(default_factory=list)
    tables: list[object] = field(default_factory=list)
    identifiers: list[object] = field(default_factory=list)

class FakeAnswerQuestionTool:
    def __init__(self, qa_result: FakeQAResult | None = None) -> None:
        self.requests = []
        self.qa_result = qa_result

    def run(self, request):
        self.requests.append(request)
        qa_result = self.qa_result or FakeQAResult(
            answer_text="Generated answer.",
            resolved_identifiers=list(request.resolved_identifiers),
            resolved_structured_entities=list(request.resolved_structured_entities),
        )
        return ToolResult.ok(data=qa_result)

class FakeRetrieveChunksTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data={
                "chunks": [{"chunk_id": "chunk-1"}],
                "context_chunks": [{"chunk_id": "chunk-1"}, {"chunk_id": "chunk-2"}],
            }
        )

class FakeRetrieveTablesTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        chunk = RetrievedChunk(
            chunk_id="chunk-table-1",
            document_id=request.document_id or "doc-42",
            content="Maintenance schedule table row",
            score=0.91,
            retrieval_source="table",
            chunk_type=ChunkType.SPARE_PARTS_TABLE,
            source=SourceLocation(page_start=12, page_end=12),
        )
        return ToolResult.ok(
            data={
                "chunks": [chunk],
                "context_chunks": [chunk],
            }
        )

class FakeRetrieveIdentifiersTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        chunk = RetrievedChunk(
            chunk_id="chunk-id-1",
            document_id=request.document_id or "doc-42",
            content="Part Number PN-001\nSerial Number SN-9001",
            score=0.95,
            retrieval_source="identifier",
            chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
            source=SourceLocation(page_start=50, page_end=50),
        )
        identifier = Identifier(
            identifier_id="identifier-1",
            document_id=request.document_id or "doc-42",
            raw_value="PN-001",
            identifier_type=IdentifierType.PART_NUMBER,
        )
        return ToolResult.ok(
            data={
                "chunks": [chunk],
                "context_chunks": [chunk],
                "identifiers": [identifier],
            }
        )

class FakeRetrieveStructuredEntitiesTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data={
                "entity_type": request.entity_type,
                "items": [
                    {
                        "name": "ACME Corp",
                        "website": "https://acme.example",
                        "source_chunk_id": "chunk-manufacturer-1",
                        "confidence_score": 0.9,
                    }
                ],
            },
            diagnostics={"total_matches": 1, "returned": 1},
        )

class FakeRetryRetrieveChunksTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        chunk = RetrievedChunk(
            chunk_id="chunk-retry-1",
            document_id=request.document_id or "doc-42",
            content="Serial Number SN-9001\nPart Number PN-001",
            score=0.9,
            retrieval_source="hybrid",
            chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
            source=SourceLocation(page_start=50, page_end=50),
        )
        return ToolResult.ok(
            data={
                "chunks": [chunk],
                "context_chunks": [chunk],
            }
        )

def test_answer_question_node_surfaces_workflow_resolved_structured_entities() -> None:
    answer_tool = FakeAnswerQuestionTool(
        qa_result=FakeQAResult(
            answer_text="Generated answer.",
            resolved_structured_entities=[
                {
                    "name": "ACME Corp",
                    "website": "https://acme.example",
                    "_entity_type": "manufacturer",
                }
            ],
        )
    )
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=answer_tool))

    patch = node(
        build_agent_state(
            user_input="what is the manufacturer website",
            document_id="doc-42",
        )
    )

    assert patch["resolved_structured_entities"][0]["website"] == "https://acme.example"

def test_answer_question_node_does_not_require_direct_structured_lookup_tool() -> None:
    answer_tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=answer_tool))

    node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            document_id="doc-42",
        )
    )

    assert answer_tool.requests[0].resolved_structured_entities == []

def test_retry_retrieval_node_preserves_existing_structured_entities_for_regeneration() -> None:
    answer_tool = FakeAnswerQuestionTool()
    retry_tool = FakeRetryRetrieveChunksTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=retry_tool,
        )
    )

    state = build_agent_state(
        user_input="what is the manufacturer website",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "what is the manufacturer website"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "Generic answer.",
            },
        }
    }
    state["reflection_result"] = {
        "decision": {
            "decision": "RETRIEVE_AGAIN",
            "reason": "Need the manufacturer website explicitly.",
        }
    }
    state["retry_query"] = "manufacturer website"
    state["initial_context_chunks"] = []
    state["resolved_structured_entities"] = [
        {
            "name": "ACME Corp",
            "website": "https://acme.example",
            "_entity_type": "manufacturer",
        }
    ]

    patch = node(state)

    assert len(answer_tool.requests[0].resolved_structured_entities) == 1
    assert patch["resolved_structured_entities"][0]["website"] == "https://acme.example"


def _retry_state_with_stale_reflection_result() -> dict:
    state = build_agent_state(
        user_input="what is the manufacturer website",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "what is the manufacturer website"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {"route": "retrieval_qa", "answer_text": "Generic answer."},
        }
    }
    # The PREVIOUS reflection pass's result -- this must not survive a
    # failed retry to be shown to the user as if it described the retry.
    state["reflection_result"] = {
        "decision": {"decision": "RETRIEVE_AGAIN", "reason": "Need the manufacturer website."},
        "overall_score": 0.4,
    }
    state["reflection_score"] = 0.4
    state["retry_query"] = "manufacturer website"
    state["initial_context_chunks"] = []
    return state


class FakeFailingRetrieveChunksTool:
    def run(self, request):
        return ToolResult.fail("Retrieval backend unavailable.", error_code="retrieval_failed")


def test_retry_retrieval_node_clears_stale_reflection_result_when_retrieve_tool_fails() -> None:
    answer_tool = FakeAnswerQuestionTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=FakeFailingRetrieveChunksTool(),
        )
    )

    patch = node(_retry_state_with_stale_reflection_result())

    assert patch["reflection_decision"] == "FAIL"
    assert patch["reflection_result"] is None
    assert patch["reflection_score"] is None


class FakeFailingAnswerQuestionTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.fail("Answer generation failed.", error_code="generation_failed")


def test_retry_retrieval_node_clears_stale_reflection_result_when_regeneration_fails() -> None:
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=FakeFailingAnswerQuestionTool(),
            retrieve_chunks_tool=FakeRetryRetrieveChunksTool(),
        )
    )

    patch = node(_retry_state_with_stale_reflection_result())

    assert patch["reflection_decision"] == "FAIL"
    assert patch["reflection_result"] is None
    assert patch["reflection_score"] is None
