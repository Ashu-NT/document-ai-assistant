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

def test_document_agent_graph_deep_research_skips_reflection_path() -> None:
    class FailingReflectionService:
        def review(self, **kwargs):
            raise AssertionError("Deep research should not enter QA reflection.")

    registry = ToolRegistry(
        find_document_tool=FakeFindDocumentTool(),
        retrieve_chunks_tool=FakeRetrieveChunksTool(),
    )
    nodes = NodeFactory(
        reflection_service=FailingReflectionService(),
    ).build_document_agent_nodes(
        tool_registry=registry,
        intent_router=DocumentAgentGraph.default_intent_router(),
        memory=None,
    )
    graph = DocumentAgentGraph(
        registry,
        nodes=nodes,
    )

    result = graph.run(
        "compare specifications and maintenance tasks",
        document_id="doc-42",
        reflection_enabled=True,
        allow_answer_generation=True,
    )

    assert result.success is True
    assert result.route == "deep_research"
    assert "Comparison Summary" in (result.response_text or "")

def test_document_agent_graph_deep_research_requests_document_clarification_when_missing() -> None:
    graph = DocumentAgentGraph(ToolRegistry(retrieve_chunks_tool=FakeRetrieveChunksTool()))

    result = graph.run("compare specifications and maintenance tasks")

    assert result.success is True
    assert result.route == "deep_research"
    assert result.data["pending_clarification"] is None
    assert "select one first" in (result.response_text or "").lower()

def test_document_agent_graph_planning_falls_back_safely_when_planner_returns_none() -> None:
    class FakePlanner:
        def create_plan(self, state):
            return None

    class FakePlannedIntentRouter:
        def route(self, user_input, *, document_id=None, document_query=None):
            return RouteDecision(
                route_type=RouteType.PLANNED_TASK,
                confidence=0.9,
                reason="Forced planned route.",
                extracted_question=user_input,
                is_compound=True,
                requires_plan=True,
            )

    router = FakePlannedIntentRouter()
    nodes = NodeFactory(planner=FakePlanner()).build_document_agent_nodes(
        tool_registry=ToolRegistry(answer_question_tool=FakeAnswerQuestionTool()),
        intent_router=router,
        memory=None,
    )
    graph = DocumentAgentGraph(
        ToolRegistry(answer_question_tool=FakeAnswerQuestionTool()),
        intent_router=router,
        nodes=nodes,
    )

    result = graph.run("compare unsupported things")

    assert result.success is True
    assert result.route == "answer_question"
