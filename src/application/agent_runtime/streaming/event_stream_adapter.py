from __future__ import annotations

from typing import Any

from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)
from src.application.agent_runtime.streaming.live_event_sink import LiveEventSink

_NODE_EVENT_MAP: dict[str, LiveAgentEventType] = {
    "route_request": LiveAgentEventType.UNDERSTAND_REQUEST,
    "retrieve_evidence": LiveAgentEventType.ACTION_COMPLETED,
    "answer_question": LiveAgentEventType.FINAL_STARTED,
    "reflect_answer": LiveAgentEventType.REFLECTION_COMPLETED,
    "final_response": LiveAgentEventType.FINAL_COMPLETED,
    "create_plan": LiveAgentEventType.PLAN_COMPLETED,
    "create_research_plan": LiveAgentEventType.PLAN_COMPLETED,
    "execute_plan": LiveAgentEventType.ACTION_COMPLETED,
    "execute_research": LiveAgentEventType.ACTION_COMPLETED,
    "synthesize_research": LiveAgentEventType.OBSERVATION,
    "research_summary": LiveAgentEventType.OBSERVATION,
    "plan_summary": LiveAgentEventType.OBSERVATION,
    "blocked_action": LiveAgentEventType.BLOCKED,
    "out_of_scope": LiveAgentEventType.BLOCKED,
    "error_handler": LiveAgentEventType.ERROR,
}


class EventStreamAdapter:
    def __init__(self, sink: LiveEventSink) -> None:
        self._sink = sink

    def run(self, compiled_graph: Any, initial_state: dict[str, Any]) -> dict[str, Any]:
        final_state: dict[str, Any] = dict(initial_state)
        for chunk in compiled_graph.stream(initial_state):
            for node_name, patch in chunk.items():
                final_state.update(patch)
                event = self._build_event(node_name, patch, final_state)
                if event is not None:
                    self._sink.emit(event)
        return final_state

    def _build_event(
        self,
        node_name: str,
        patch: dict[str, Any],
        state: dict[str, Any],
    ) -> LiveAgentEvent | None:
        event_type = _NODE_EVENT_MAP.get(node_name)
        if event_type is None:
            return None
        payload = self._extract_payload(event_type, patch, state)
        return LiveAgentEvent(event_type=event_type, payload=payload)

    def _extract_payload(
        self,
        event_type: LiveAgentEventType,
        patch: dict[str, Any],
        state: dict[str, Any],
    ) -> dict[str, Any]:
        if event_type == LiveAgentEventType.UNDERSTAND_REQUEST:
            return {"route": state.get("route_type") or state.get("route") or ""}
        if event_type == LiveAgentEventType.PLAN_COMPLETED:
            plan = state.get("research_plan") or state.get("execution_plan") or {}
            tasks = plan.get("tasks", []) if isinstance(plan, dict) else []
            return {"task_count": len(tasks)}
        if event_type == LiveAgentEventType.ACTION_COMPLETED:
            chunks = state.get("context_chunks") or []
            return {"chunk_count": len(chunks) if isinstance(chunks, list) else 0}
        if event_type == LiveAgentEventType.REFLECTION_COMPLETED:
            return {"decision": str(state.get("reflection_decision") or "")}
        if event_type == LiveAgentEventType.ERROR:
            return {"message": str(state.get("error") or "")}
        if event_type == LiveAgentEventType.BLOCKED:
            return {
                "reason": str(
                    state.get("blocked_reason")
                    or state.get("guardrail_user_message")
                    or ""
                )
            }
        return {}
