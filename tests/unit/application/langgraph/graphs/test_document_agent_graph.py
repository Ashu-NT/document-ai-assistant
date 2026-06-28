from dataclasses import dataclass, field

from src.application.langgraph import DocumentAgentGraph, ToolRegistry
from src.application.tools.common import ToolResult


@dataclass(slots=True)
class FakeQAResult:
    answer_text: str | None = None
    safe_user_message: str | None = None


@dataclass(slots=True)
class FakeExplorationOverview:
    title: str | None = "Pump Manual"
    file_name: str = "pump_manual.pdf"


@dataclass(slots=True)
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
    def run(self, request):
        return ToolResult.ok(
            data={"document_id": "doc-42", "display_name": "Pump Manual"}
        )


class FakeExploreDocumentTool:
    def run(self, request):
        return ToolResult.ok(data=FakeExplorationResult())


class FakeAnswerQuestionTool:
    def run(self, request):
        return ToolResult.ok(data=FakeQAResult(answer_text="The interval is 500 hours."))


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


def test_document_agent_graph_exploration_path_works() -> None:
    graph = DocumentAgentGraph(
        ToolRegistry(
            find_document_tool=FakeFindDocumentTool(),
            explore_document_tool=FakeExploreDocumentTool(),
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
    assert result.route == "needs_clarification"
    assert "specify" in (result.response_text or "").lower()
