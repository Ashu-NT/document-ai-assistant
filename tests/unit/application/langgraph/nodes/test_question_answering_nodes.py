from dataclasses import dataclass, field

from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.question_answering import (
    AnswerQuestionNode,
    ExploreDocumentNode,
    RetrieveEvidenceNode,
)
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult


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
