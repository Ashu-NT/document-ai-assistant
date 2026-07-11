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

def test_retry_retrieval_node_preserves_resolved_identifiers_for_regeneration() -> None:
    answer_tool = FakeAnswerQuestionTool()
    retry_tool = FakeRetryRetrieveChunksTool()
    node = RetryRetrievalNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=retry_tool,
        )
    )

    state = build_agent_state(
        user_input="list all serial and part nmubers",
        document_id="doc-42",
        selected_document_id="doc-42",
        allow_answer_generation=True,
        include_context=True,
    )
    state["question"] = "list all serial and part nmubers"
    state["route"] = "answer_question"
    state["tool_results"] = {
        "answer_question": {
            "success": True,
            "data": {
                "route": "retrieval_qa",
                "answer_text": "Generic answer.",
                "answer_intent": "identifier_lookup",
            },
        }
    }
    state["reflection_result"] = {
        "decision": {
            "decision": "RETRIEVE_AGAIN",
            "reason": "Need explicit identifier values.",
        }
    }
    state["retry_query"] = "serial number part number identifier list"
    state["resolved_identifiers"] = [
        {
            "identifier_id": "identifier-1",
            "document_id": "doc-42",
            "raw_value": "PN-001",
            "identifier_type": "part_number",
        }
    ]
    state["initial_context_chunks"] = []

    patch = node(state)

    assert retry_tool.requests
    assert len(answer_tool.requests[0].resolved_identifiers) == 1
    assert answer_tool.requests[0].resolved_identifiers[0].raw_value == "PN-001"
    assert patch["resolved_identifiers"][0]["raw_value"] == "PN-001"
