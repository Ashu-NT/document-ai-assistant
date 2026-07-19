from __future__ import annotations

from typing import Any

from src.application.agent_runtime.streaming.answer_question_event_narrator import (
    build_answer_question_observation_payload,
    build_answer_question_retrieve_payload,
)
from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)
from src.application.agent_runtime.streaming.live_event_sink import LiveEventSink
from src.application.agent_runtime.streaming.research_event_narrator import (
    build_evaluate_payload,
)

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
    "evaluate_research": LiveAgentEventType.OBSERVATION,
    "synthesize_research": LiveAgentEventType.OBSERVATION,
    "plan_summary": LiveAgentEventType.OBSERVATION,
    "blocked_action": LiveAgentEventType.BLOCKED,
    "out_of_scope": LiveAgentEventType.BLOCKED,
    "error_handler": LiveAgentEventType.ERROR,
    # Every remaining node the graph can actually route through (query-to-
    # retrieval flow follow-up: "all steps," not just the answer-generation
    # path, must produce a visible live event) -- previously silent, so
    # these steps printed nothing at all when they ran.
    "find_document": LiveAgentEventType.ACTION_COMPLETED,
    "list_documents": LiveAgentEventType.ACTION_COMPLETED,
    "document_details": LiveAgentEventType.ACTION_COMPLETED,
    "explore_document": LiveAgentEventType.ACTION_COMPLETED,
    "run_quality_gate": LiveAgentEventType.ACTION_COMPLETED,
    "retrieval_trace": LiveAgentEventType.ACTION_COMPLETED,
    "session_command": LiveAgentEventType.ACTION_COMPLETED,
    "retry_retrieval": LiveAgentEventType.ACTION_COMPLETED,
    "research_summary": LiveAgentEventType.OBSERVATION,
    "clarify_request": LiveAgentEventType.CLARIFY,
}

# Nodes whose only job is "call a tool, stash the result under
# tool_results[node_name]" (serialize_tool_result()'s uniform
# success/message/error_code/diagnostics/metadata/data shape) -- one
# generic extraction path instead of one bespoke branch per node.
_GENERIC_TOOL_ACTION_NODES = frozenset(
    {
        "find_document",
        "list_documents",
        "document_details",
        "explore_document",
        "run_quality_gate",
        "retrieval_trace",
    }
)


class EventStreamAdapter:
    def __init__(self, sink: LiveEventSink) -> None:
        self._sink = sink

    def run(self, compiled_graph: Any, initial_state: dict[str, Any]) -> dict[str, Any]:
        final_state: dict[str, Any] = dict(initial_state)
        for chunk in compiled_graph.stream(initial_state):
            for node_name, patch in chunk.items():
                final_state.update(patch)
                for event in self._build_events(node_name, patch, final_state):
                    self._sink.emit(event)
        return final_state

    def _build_events(
        self,
        node_name: str,
        patch: dict[str, Any],
        state: dict[str, Any],
    ) -> list[LiveAgentEvent]:
        events: list[LiveAgentEvent] = []
        if node_name == "answer_question":
            retrieve_payload = build_answer_question_retrieve_payload(state)
            if retrieve_payload is not None:
                events.append(
                    LiveAgentEvent(
                        event_type=LiveAgentEventType.ACTION_COMPLETED,
                        payload=retrieve_payload,
                    )
                )
            observation_payload = build_answer_question_observation_payload(state)
            if observation_payload is not None:
                events.append(
                    LiveAgentEvent(
                        event_type=LiveAgentEventType.OBSERVATION,
                        payload=observation_payload,
                    )
                )
        event_type = _NODE_EVENT_MAP.get(node_name)
        if event_type is None:
            return events
        payload = self._extract_payload(event_type, node_name, patch, state)
        events.append(LiveAgentEvent(event_type=event_type, payload=payload))
        return events

    def _extract_payload(
        self,
        event_type: LiveAgentEventType,
        node_name: str,
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
            if node_name in _GENERIC_TOOL_ACTION_NODES:
                tool_result = (state.get("tool_results") or {}).get(node_name) or {}
                description = str(tool_result.get("message") or "").strip() or (
                    f"Ran {node_name.replace('_', ' ')}."
                )
                return {"description": description}
            if node_name == "session_command":
                description = str(patch.get("response_text") or "").strip() or (
                    "Session command completed."
                )
                return {"description": description}
            if node_name == "retry_retrieval":
                retry_query = str(state.get("retry_query") or "").strip()
                description = (
                    f"Retrying retrieval: {retry_query}"
                    if retry_query
                    else "Retrying retrieval with a refined query."
                )
                return {"description": description}
            chunks = state.get("context_chunks") or []
            count = len(chunks) if isinstance(chunks, list) else 0
            description = _build_retrieve_description(chunks)
            return {"chunk_count": count, "description": description}
        if event_type == LiveAgentEventType.OBSERVATION:
            if node_name == "evaluate_research":
                return build_evaluate_payload(state)
            if node_name == "research_summary":
                detail = str(patch.get("response_text") or "").strip()
                return {
                    "kind": "observation",
                    "detail": detail[:300] if detail else "Research summary prepared.",
                }
            detail = (
                str(patch.get("synthesis") or "").strip()
                or str(patch.get("summary") or "").strip()
                or str(state.get("research_summary") or "").strip()
            )
            if not detail:
                chunks = state.get("context_chunks") or []
                count = len(chunks) if isinstance(chunks, list) else 0
                detail = f"Processed {count} evidence group(s)." if count else "Evidence gathered."
            return {"kind": "observation", "detail": detail[:300]}
        if event_type == LiveAgentEventType.CLARIFY:
            question = str(
                patch.get("clarification_question")
                or state.get("clarification_question")
                or ""
            ).strip()
            return {"question": question}
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
