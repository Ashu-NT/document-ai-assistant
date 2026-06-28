from dataclasses import dataclass

from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.nodes.documents import (
    FindDocumentNode,
    ListDocumentsNode,
)
from src.application.langgraph.state import build_agent_state
from src.application.tools.common import ToolResult


class FakeListDocumentsTool:
    def __init__(self) -> None:
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return ToolResult.ok(
            data=[{"document_id": "doc-1", "display_name": "Manual"}],
            message="Found 1 document(s).",
        )


class FakeFindDocumentTool:
    def __init__(self, *, result: ToolResult) -> None:
        self.result = result
        self.requests = []

    def run(self, request):
        self.requests.append(request)
        return self.result


def test_list_documents_node_calls_list_documents_tool() -> None:
    tool = FakeListDocumentsTool()
    node = ListDocumentsNode(ToolRegistry(list_documents_tool=tool))

    patch = node(build_agent_state(user_input="list documents"))

    assert tool.requests
    assert patch["response_text"] == "Found 1 document(s)."
    assert patch["tool_results"]["list_documents"]["success"] is True


def test_find_document_node_sets_document_id_on_single_match() -> None:
    result = ToolResult.ok(
        data={"document_id": "doc-42", "display_name": "Pump Manual"},
    )
    node = FindDocumentNode(
        ToolRegistry(find_document_tool=FakeFindDocumentTool(result=result))
    )

    patch = node(
        build_agent_state(
            user_input="find document pump",
            document_query="pump",
        )
    )

    assert patch["document_id"] == "doc-42"
    assert patch["document_title"] == "Pump Manual"


def test_find_document_node_asks_for_clarification_on_multiple_matches() -> None:
    result = ToolResult.fail(
        "Multiple documents matched the query.",
        error_code="multiple_documents_found",
        diagnostics={
            "matches": [
                {"document_id": "doc-1", "display_name": "Pump Manual"},
                {"document_id": "doc-2", "display_name": "Pump Guide"},
            ]
        },
    )
    node = FindDocumentNode(
        ToolRegistry(find_document_tool=FakeFindDocumentTool(result=result))
    )

    patch = node(
        build_agent_state(
            user_input="find document pump",
            document_query="pump",
        )
    )

    assert patch["needs_clarification"] is True
    assert "Pump Manual" in patch["clarification_message"]
