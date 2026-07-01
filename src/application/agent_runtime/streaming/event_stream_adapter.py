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
            return {
                "route": str(state.get("route_type") or state.get("route") or ""),
                "intent": str(state.get("answer_intent") or ""),
            }
        if event_type == LiveAgentEventType.PLAN_COMPLETED:
            plan = state.get("research_plan") or state.get("execution_plan") or {}
            tasks = plan.get("tasks", []) if isinstance(plan, dict) else []
            titles = [
                str(t.get("title") or t.get("description") or "").strip()
                for t in tasks
                if isinstance(t, dict) and (t.get("title") or t.get("description"))
            ]
            return {"task_count": len(tasks), "task_titles": titles}
        if event_type == LiveAgentEventType.ACTION_COMPLETED:
            chunks = state.get("context_chunks") or []
            count = len(chunks) if isinstance(chunks, list) else 0
            description = _build_retrieve_description(chunks)
            return {"chunk_count": count, "description": description}
        if event_type == LiveAgentEventType.OBSERVATION:
            detail = (
                str(patch.get("synthesis") or "").strip()
                or str(patch.get("summary") or "").strip()
                or str(state.get("research_summary") or "").strip()
            )
            if not detail:
                chunks = state.get("context_chunks") or []
                count = len(chunks) if isinstance(chunks, list) else 0
                detail = f"Processed {count} evidence group(s)." if count else "Evidence gathered."
            return {"detail": detail[:300]}
        if event_type == LiveAgentEventType.REFLECTION_COMPLETED:
            reflection_result = state.get("reflection_result") or {}
            decision_obj = (
                reflection_result.get("decision") or {}
                if isinstance(reflection_result, dict)
                else {}
            )
            decision = (
                (decision_obj.get("decision") if isinstance(decision_obj, dict) else None)
                or state.get("reflection_decision")
                or ""
            )
            reason = (
                decision_obj.get("reason") or ""
                if isinstance(decision_obj, dict)
                else ""
            )
            return {"decision": str(decision), "reason": str(reason)}
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


def _build_retrieve_description(chunks: list) -> str:
    if not isinstance(chunks, list) or not chunks:
        return ""
    count = len(chunks)
    pages: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        source = chunk.get("source") or {}
        if not isinstance(source, dict):
            continue
        pg = source.get("page_start")
        if pg is not None:
            pg_str = str(pg)
            if pg_str not in pages:
                pages.append(pg_str)
        if len(pages) >= 3:
            break
    if pages:
        return f"Retrieved {count} evidence chunk(s) from p.{', p.'.join(pages)}."
    return f"Retrieved {count} evidence chunk(s)."
