import pytest

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories import ToolRegistry


class DummyTool:
    pass


def test_tool_registry_returns_registered_tool() -> None:
    tool = DummyTool()
    registry = ToolRegistry(list_documents_tool=tool)

    assert registry.get("list_documents") is tool
    assert registry.maybe("list_documents") is tool
    assert registry.require("list_documents") is tool


def test_tool_registry_fails_clearly_for_missing_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(GraphError) as exc_info:
        registry.require("answer_question")

    assert exc_info.value.error_code == "tool_not_available"
