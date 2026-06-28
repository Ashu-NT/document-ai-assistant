from __future__ import annotations

from src.application.tools.common.tool_metadata import ToolMetadata
from src.application.tools.common.tool_result import ToolResult
from src.shared.exceptions import ApplicationError


def application_error_result(
    exc: ApplicationError,
    *,
    metadata: ToolMetadata,
    fallback_error_code: str | None = None,
) -> ToolResult:
    return ToolResult.fail(
        exc.message,
        error_code=fallback_error_code or exc.error_code,
        diagnostics=dict(exc.details),
        metadata=metadata,
    )


def invalid_request_result(
    message: str,
    *,
    metadata: ToolMetadata,
    diagnostics: dict | None = None,
) -> ToolResult:
    return ToolResult.fail(
        message,
        error_code="invalid_request",
        diagnostics=diagnostics or {},
        metadata=metadata,
    )


def not_implemented_result(
    *,
    metadata: ToolMetadata,
    message: str,
) -> ToolResult:
    return ToolResult.fail(
        message,
        error_code="not_implemented",
        metadata=metadata,
    )
