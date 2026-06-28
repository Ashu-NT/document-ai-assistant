from src.application.tools.common import ToolMetadata, ToolResult


def test_tool_result_ok_creates_success_result():
    metadata = ToolMetadata(tool_name="demo", category="test")

    result = ToolResult.ok(
        data={"value": 1},
        message="done",
        diagnostics={"count": 1},
        metadata=metadata,
    )

    assert result.success is True
    assert result.data == {"value": 1}
    assert result.message == "done"
    assert result.error_code is None
    assert result.diagnostics == {"count": 1}
    assert result.metadata == metadata


def test_tool_result_fail_creates_failure_result():
    metadata = ToolMetadata(tool_name="demo", category="test")

    result = ToolResult.fail(
        "broken",
        error_code="invalid_request",
        diagnostics={"field": "question"},
        metadata=metadata,
    )

    assert result.success is False
    assert result.message == "broken"
    assert result.error_code == "invalid_request"
    assert result.diagnostics == {"field": "question"}
    assert result.metadata == metadata
