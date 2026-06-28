from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.tools.common.tool_metadata import ToolMetadata


@dataclass(slots=True)
class ToolResult:
    success: bool
    data: Any | None = None
    message: str | None = None
    error_code: str | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)
    metadata: ToolMetadata | None = None

    @classmethod
    def ok(
        cls,
        *,
        data: Any | None = None,
        message: str | None = None,
        diagnostics: dict[str, Any] | None = None,
        metadata: ToolMetadata | None = None,
    ) -> "ToolResult":
        return cls(
            success=True,
            data=data,
            message=message,
            diagnostics=diagnostics or {},
            metadata=metadata,
        )

    @classmethod
    def fail(
        cls,
        message: str,
        *,
        error_code: str | None = None,
        diagnostics: dict[str, Any] | None = None,
        metadata: ToolMetadata | None = None,
        data: Any | None = None,
    ) -> "ToolResult":
        return cls(
            success=False,
            data=data,
            message=message,
            error_code=error_code,
            diagnostics=diagnostics or {},
            metadata=metadata,
        )
