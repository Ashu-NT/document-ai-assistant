from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from src.application.langgraph.tracing.langgraph_trace import LangGraphTrace


@dataclass(slots=True, frozen=True)
class _TraceToken:
    node_name: str
    route: str | None
    tool_name: str | None
    started_at: str
    started_counter: float


class GraphRunRecorder:
    def start_node(
        self,
        node_name: str,
        *,
        route: str | None = None,
        tool_name: str | None = None,
    ) -> _TraceToken:
        return _TraceToken(
            node_name=node_name,
            route=route,
            tool_name=tool_name,
            started_at=datetime.now(timezone.utc).isoformat(),
            started_counter=perf_counter(),
        )

    def finish_node(
        self,
        token: _TraceToken,
        *,
        success: bool,
        error_code: str | None = None,
        diagnostics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        finished_at = datetime.now(timezone.utc).isoformat()
        elapsed_ms = round((perf_counter() - token.started_counter) * 1000, 3)
        return LangGraphTrace(
            node_name=token.node_name,
            started_at=token.started_at,
            finished_at=finished_at,
            elapsed_ms=elapsed_ms,
            route=token.route,
            success=success,
            tool_name=token.tool_name,
            error_code=error_code,
            diagnostics=diagnostics or {},
        ).to_dict()
