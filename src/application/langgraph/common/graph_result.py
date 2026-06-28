from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any


def serialize_graph_value(value: Any) -> Any:
    if is_dataclass(value):
        return serialize_graph_value(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): serialize_graph_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple | set | frozenset):
        return [serialize_graph_value(item) for item in value]
    return value


@dataclass(slots=True)
class GraphResult:
    success: bool
    response_text: str | None = None
    data: dict[str, Any] | None = None
    route: str | None = None
    error_code: str | None = None
    diagnostics: dict[str, Any] | None = None
    trace: list[dict[str, Any]] | None = None
    messages: list[dict[str, Any]] | None = None

    @classmethod
    def ok(
        cls,
        *,
        response_text: str | None = None,
        data: dict[str, Any] | None = None,
        route: str | None = None,
        diagnostics: dict[str, Any] | None = None,
        trace: list[dict[str, Any]] | None = None,
        messages: list[dict[str, Any]] | None = None,
    ) -> "GraphResult":
        return cls(
            success=True,
            response_text=response_text,
            data=data or {},
            route=route,
            diagnostics=diagnostics or {},
            trace=trace or [],
            messages=messages or [],
        )

    @classmethod
    def fail(
        cls,
        *,
        response_text: str | None = None,
        error_code: str | None = None,
        data: dict[str, Any] | None = None,
        route: str | None = None,
        diagnostics: dict[str, Any] | None = None,
        trace: list[dict[str, Any]] | None = None,
        messages: list[dict[str, Any]] | None = None,
    ) -> "GraphResult":
        return cls(
            success=False,
            response_text=response_text,
            data=data or {},
            route=route,
            error_code=error_code,
            diagnostics=diagnostics or {},
            trace=trace or [],
            messages=messages or [],
        )

    def to_dict(self) -> dict[str, Any]:
        return serialize_graph_value(
            {
                "success": self.success,
                "response_text": self.response_text,
                "data": self.data or {},
                "route": self.route,
                "error_code": self.error_code,
                "diagnostics": self.diagnostics or {},
                "trace": self.trace or [],
                "messages": self.messages or [],
            }
        )
