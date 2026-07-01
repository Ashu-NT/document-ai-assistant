from __future__ import annotations

import sys
from typing import Any, TextIO

from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)

_EVENT_LABELS: dict[LiveAgentEventType, str] = {
    LiveAgentEventType.RUN_STARTED: "Starting",
    LiveAgentEventType.UNDERSTAND_REQUEST: "Routing request",
    LiveAgentEventType.STRATEGY_STARTED: "Selecting retrieval strategy",
    LiveAgentEventType.STRATEGY_COMPLETED: "Strategy selected",
    LiveAgentEventType.PLAN_STARTED: "Creating plan",
    LiveAgentEventType.PLAN_COMPLETED: "Plan ready",
    LiveAgentEventType.ACTION_STARTED: "Retrieving evidence",
    LiveAgentEventType.ACTION_COMPLETED: "Evidence collected",
    LiveAgentEventType.OBSERVATION: "Processing evidence",
    LiveAgentEventType.REFLECTION_STARTED: "Reviewing answer",
    LiveAgentEventType.REFLECTION_COMPLETED: "Review complete",
    LiveAgentEventType.FINAL_STARTED: "Generating grounded answer",
    LiveAgentEventType.FINAL_COMPLETED: "Answer ready",
    LiveAgentEventType.RUN_COMPLETED: "Done",
    LiveAgentEventType.ERROR: "Error",
    LiveAgentEventType.BLOCKED: "Request blocked",
}


class ConsoleLiveEventSink:
    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stdout

    def emit(self, event: LiveAgentEvent) -> None:
        label = _EVENT_LABELS.get(event.event_type)
        if label is None:
            return
        detail = _event_detail(event)
        if detail:
            print(f"{label}: {detail}...", file=self._stream, flush=True)
        else:
            print(f"{label}...", file=self._stream, flush=True)


def _event_detail(event: LiveAgentEvent) -> str:
    payload: dict[str, Any] = event.payload or {}
    if event.event_type == LiveAgentEventType.UNDERSTAND_REQUEST:
        route = str(payload.get("route") or "").replace("_", " ").strip()
        return route
    if event.event_type == LiveAgentEventType.STRATEGY_COMPLETED:
        return str(payload.get("strategy") or "").strip()
    if event.event_type == LiveAgentEventType.PLAN_COMPLETED:
        count = payload.get("task_count")
        return f"{count} task(s)" if count else ""
    if event.event_type == LiveAgentEventType.REFLECTION_COMPLETED:
        return str(payload.get("decision") or "").strip()
    if event.event_type == LiveAgentEventType.ACTION_COMPLETED:
        count = payload.get("chunk_count")
        return f"{count} chunk(s)" if count else ""
    if event.event_type == LiveAgentEventType.ERROR:
        return str(payload.get("message") or "").strip()
    if event.event_type == LiveAgentEventType.BLOCKED:
        return str(payload.get("reason") or "").strip()
    return ""
