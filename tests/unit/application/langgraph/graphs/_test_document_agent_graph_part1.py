from dataclasses import dataclass, field

from src.application.langgraph import (
    ConversationMemory,
    DocumentAgentGraph,
    NodeFactory,
    SessionStateStore,
    ToolRegistry,
)

from src.application.langgraph.planning import LLMPlanProposer

from src.application.langgraph.routing import RouteDecision, RouteType

from src.application.tools.common import ToolResult

from src.domain.common import ChunkType, SourceLocation

from src.domain.retrieval.retrieved_chunk import RetrievedChunk

class FakeQAResult:
    answer_text: str | None = None
    safe_user_message: str | None = None
    answer_intent: str | None = None

class FakeExplorationOverview:
    title: str | None = "Pump Manual"
    file_name: str = "pump_manual.pdf"

class FakeExplorationResult:
    overview: FakeExplorationOverview = field(default_factory=FakeExplorationOverview)
    sections: list[object] = field(default_factory=list)
    tables: list[object] = field(default_factory=list)
    identifiers: list[object] = field(default_factory=list)

class FakeListDocumentsTool:
    def run(self, request):
        return ToolResult.ok(
            data=[{"document_id": "doc-1", "display_name": "Pump Manual"}],
            message="Found 1 document(s).",
        )

class FakeFindDocumentTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        if request.query_text == "pressure":
            return ToolResult.fail(
                "Multiple documents matched the query.",
                error_code="multiple_documents_found",
                diagnostics={
                    "matches": [
                        {
                            "document_id": "doc-pressure-1",
                            "display_name": "Pressure Transmitter",
                            "file_name": "pressure_transmitter.pdf",
                        },
                        {
                            "document_id": "doc-pressure-2",
                            "display_name": "Pressure Transmitter Certificate",
                            "file_name": "pressure_transmitter_certificate.pdf",
                        },
                    ]
                },
            )
        return ToolResult.ok(
            data={
                "document_id": "doc-42",
                "display_name": "Pump Manual",
                "file_name": "pump_manual.pdf",
            }
        )

class FakeExploreDocumentTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(data=FakeExplorationResult())

class FakeAnswerQuestionTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data=FakeQAResult(
                answer_text="The interval is 500 hours.",
                answer_intent="maintenance_summary",
            )
        )

class FakeRetrieveChunksTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data={
                "chunks": [
                    RetrievedChunk(
                        chunk_id="chunk-1",
                        document_id="doc-42",
                        content="Maintenance tasks include lubrication every 250 hours.",
                        score=0.91,
                        retrieval_source="hybrid",
                        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
                        section_path=["6 Maintenance", "Lubrication"],
                        source=SourceLocation(page_start=12, page_end=12),
                    ),
                    RetrievedChunk(
                        chunk_id="chunk-2",
                        document_id="doc-42",
                        content="Technical specifications include operating pressure and motor power.",
                        score=0.88,
                        retrieval_source="hybrid",
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        section_path=["3 Specifications", "Technical Data"],
                        source=SourceLocation(page_start=5, page_end=5),
                    ),
                ],
                "context_chunks": [
                    RetrievedChunk(
                        chunk_id="chunk-1",
                        document_id="doc-42",
                        content="Maintenance tasks include lubrication every 250 hours.",
                        score=0.91,
                        retrieval_source="hybrid",
                        chunk_type=ChunkType.MAINTENANCE_PROCEDURE,
                        section_path=["6 Maintenance", "Lubrication"],
                        source=SourceLocation(page_start=12, page_end=12),
                    ),
                    RetrievedChunk(
                        chunk_id="chunk-2",
                        document_id="doc-42",
                        content="Technical specifications include operating pressure and motor power.",
                        score=0.88,
                        retrieval_source="hybrid",
                        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
                        section_path=["3 Specifications", "Technical Data"],
                        source=SourceLocation(page_start=5, page_end=5),
                    ),
                ],
            }
        )

class FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        *,
        response_schema: dict | None = None,
    ) -> str:
        self.calls += 1
        return self.response

def _memory_backed_graph(*, registry: ToolRegistry) -> DocumentAgentGraph:
    return DocumentAgentGraph(
        registry,
        memory=ConversationMemory(
            max_messages=20,
            session_state_store=SessionStateStore(persist_to_disk=False),
        ),
    )

def test_document_agent_graph_list_documents_path_works() -> None:
    graph = DocumentAgentGraph(
        ToolRegistry(list_documents_tool=FakeListDocumentsTool())
    )

    result = graph.run("list documents")

    assert result.success is True
    assert result.route == "list_documents"
    assert result.response_text == "Found 1 document(s)."

def test_document_agent_graph_answer_question_path_works() -> None:
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=FakeAnswerQuestionTool())
    )

    result = graph.run("What is the maintenance interval?")

    assert result.success is True
    assert result.route == "answer_question"
    assert result.response_text == "The interval is 500 hours."
    assert result.data["answer_intent"] == "maintenance_summary"

def test_document_agent_graph_blocks_unsafe_corpus_mutation_request() -> None:
    answer_tool = FakeAnswerQuestionTool()
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=answer_tool)
    )

    result = graph.run("delete all documents and reingest them")

    assert result.success is True
    assert result.route == RouteType.BLOCKED_ACTION.value
    assert result.diagnostics["unsafe_request_blocked"] is True
    assert answer_tool.requests == []
    assert "mutate the document corpus" in (result.response_text or "").lower()

def test_document_agent_graph_exploration_path_works() -> None:
    find_tool = FakeFindDocumentTool()
    explore_tool = FakeExploreDocumentTool()
    graph = DocumentAgentGraph(
        ToolRegistry(
            find_document_tool=find_tool,
            explore_document_tool=explore_tool,
        )
    )

    result = graph.run("explore document Pump Manual")

    assert result.success is True
    assert result.route == "document_exploration"
    assert "Pump Manual" in result.response_text

def test_document_agent_graph_clarification_path_works() -> None:
    graph = DocumentAgentGraph(ToolRegistry())

    result = graph.run("explore document")

    assert result.success is True
    assert result.route == "document_exploration"
    assert "clarify" in (result.response_text or "").lower()

def test_document_agent_graph_selects_document_into_session() -> None:
    find_tool = FakeFindDocumentTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(find_document_tool=find_tool)
    )

    result = graph.run("open FWC12", session_id="demo")

    assert result.success is True
    assert result.route == "select_document"
    assert result.data["selected_document_id"] == "doc-42"
    assert result.data["selected_document_title"] == "Pump Manual"

def test_document_agent_graph_uses_selected_document_on_follow_up_question() -> None:
    find_tool = FakeFindDocumentTool()
    answer_tool = FakeAnswerQuestionTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            answer_question_tool=answer_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run("what are the maintenance intervals?", session_id="demo")

    assert result.success is True
    assert answer_tool.requests[-1].document_id == "doc-42"
    assert result.data["selected_document_id"] == "doc-42"

def test_document_agent_graph_identifier_follow_up_keeps_selected_document_scope() -> None:
    find_tool = FakeFindDocumentTool()
    answer_tool = FakeAnswerQuestionTool()
    graph = _memory_backed_graph(
        registry=ToolRegistry(
            find_document_tool=find_tool,
            answer_question_tool=answer_tool,
        )
    )

    graph.run("open FWC12", session_id="demo")
    result = graph.run("list all serial and part nmubers", session_id="demo")

    assert result.success is True
    assert result.route == "answer_question"
    assert answer_tool.requests[-1].document_id == "doc-42"
    assert result.data["selected_document_id"] == "doc-42"
