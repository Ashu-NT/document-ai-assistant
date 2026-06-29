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
    plan_id: str | None
    plan_goal: str | None
    step_id: str | None
    selected_document_id: str | None
    started_at: str
    started_counter: float


class GraphRunRecorder:
    def start_node(
        self,
        node_name: str,
        *,
        route: str | None = None,
        tool_name: str | None = None,
        plan_id: str | None = None,
        plan_goal: str | None = None,
        step_id: str | None = None,
        selected_document_id: str | None = None,
    ) -> _TraceToken:
        return _TraceToken(
            node_name=node_name,
            route=route,
            tool_name=tool_name,
            plan_id=plan_id,
            plan_goal=plan_goal,
            step_id=step_id,
            selected_document_id=selected_document_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            started_counter=perf_counter(),
        )

    def finish_node(
        self,
        token: _TraceToken,
        *,
        success: bool,
        error_code: str | None = None,
        fallback_reason: str | None = None,
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
            plan_id=token.plan_id,
            plan_goal=token.plan_goal,
            step_id=token.step_id,
            selected_document_id=token.selected_document_id,
            fallback_reason=fallback_reason,
            error_code=error_code,
            diagnostics=diagnostics or {},
        ).to_dict()
