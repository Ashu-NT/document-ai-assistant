from dataclasses import dataclass, field

from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.question_answering import (
    AnswerQuestionNode,
    ExploreDocumentNode,
    RetrieveEvidenceNode,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult
from src.domain.common import ChunkType, SourceLocation
from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True)
class FakeQAResult:
    answer_text: str | None = None
    safe_user_message: str | None = None


@dataclass(slots=True)
class FakeExplorationResult:
    overview: object
    sections: list[object] = field(default_factory=list)
    tables: list[object] = field(default_factory=list)
    identifiers: list[object] = field(default_factory=list)


class FakeAnswerQuestionTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(data=FakeQAResult(answer_text="Generated answer."))


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


def test_answer_question_node_calls_tool_with_document_id() -> None:
    tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=tool))

    patch = node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            document_id="doc-42",
        )
    )

    assert tool.requests[0].document_id == "doc-42"
    assert patch["response_text"] == "Generated answer."


def test_explore_document_node_requires_document_id() -> None:
    node = ExploreDocumentNode(ToolRegistry())

    patch = node(build_agent_state(user_input="explore document"))

    assert patch["needs_clarification"] is True


def test_retrieve_evidence_node_calls_retrieve_chunks_tool() -> None:
    tool = FakeRetrieveChunksTool()
    node = RetrieveEvidenceNode(ToolRegistry(retrieve_chunks_tool=tool))

    patch = node(
        build_agent_state(
            user_input="retrieve shaft seal lubrication",
            document_id="doc-42",
            top_k=3,
        )
    )

    assert tool.requests[0].document_id == "doc-42"
    assert tool.requests[0].top_k == 3
    assert "Retrieved 1 evidence chunk" in patch["response_text"]


def test_answer_question_node_uses_selected_document_when_request_document_missing() -> None:
    tool = FakeAnswerQuestionTool()
    node = AnswerQuestionNode(ToolRegistry(answer_question_tool=tool))

    node(
        build_agent_state(
            user_input="What is the maintenance interval?",
            selected_document_id="doc-selected",
            selected_document_title="FWC12 Manual",
        )
    )

    assert tool.requests[0].document_id == "doc-selected"


def test_retrieve_evidence_node_uses_strategy_selected_table_tool_when_requested() -> None:
    chunk_tool = FakeRetrieveChunksTool()
    table_tool = FakeRetrieveTablesTool()
    node = RetrieveEvidenceNode(
        ToolRegistry(
            retrieve_chunks_tool=chunk_tool,
            retrieve_tables_tool=table_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
    )

    patch = node(
        build_agent_state(
            user_input="show maintenance table",
            document_id="doc-42",
            top_k=3,
            retrieval_strategy_enabled=True,
            requested_retrieval_strategy="table",
        )
    )

    assert table_tool.requests
    assert patch["retrieval_strategy_decision"]["primary_strategy"] == "TABLE_LOOKUP"
    assert "Retrieved 1 evidence chunk" in patch["response_text"]


def test_answer_question_node_passes_strategy_selected_chunks_as_override() -> None:
    answer_tool = FakeAnswerQuestionTool()
    table_tool = FakeRetrieveTablesTool()
    node = AnswerQuestionNode(
        ToolRegistry(
            answer_question_tool=answer_tool,
            retrieve_chunks_tool=FakeRetrieveChunksTool(),
            retrieve_tables_tool=table_tool,
        ),
        retrieval_strategy_service=RetrievalStrategyService(),
        retrieval_plan_executor=RetrievalPlanExecutor(),
        retrieval_strategy_policy=RetrievalStrategyPolicy(enabled=True),
    )

    node(
        build_agent_state(
            user_input="show maintenance table",
            document_id="doc-42",
            retrieval_strategy_enabled=True,
            requested_retrieval_strategy="table",
        )
    )

    assert table_tool.requests
    assert answer_tool.requests[0].context_override_chunks is not None
    assert len(answer_tool.requests[0].context_override_chunks) == 1
