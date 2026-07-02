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
    "evaluate_research": LiveAgentEventType.OBSERVATION,
    "synthesize_research": LiveAgentEventType.OBSERVATION,
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
            retrieve_payload = _build_answer_question_retrieve_payload(state)
            if retrieve_payload is not None:
                events.append(
                    LiveAgentEvent(
                        event_type=LiveAgentEventType.ACTION_COMPLETED,
                        payload=retrieve_payload,
                    )
                )
            observation_payload = _build_answer_question_observation_payload(state)
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
            chunks = state.get("context_chunks") or []
            count = len(chunks) if isinstance(chunks, list) else 0
            description = _build_retrieve_description(chunks)
            return {"chunk_count": count, "description": description}
        if event_type == LiveAgentEventType.OBSERVATION:
            if node_name == "evaluate_research":
                return _build_evaluate_payload(state)
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


def _build_evaluate_payload(state: dict[str, Any]) -> dict[str, Any]:
    research_trace = state.get("research_trace") or {}
    coverage = (
        research_trace.get("strategy_coverage") or {}
        if isinstance(research_trace, dict)
        else {}
    )
    ratio = coverage.get("ratio") if isinstance(coverage, dict) else None
    uncovered = coverage.get("uncovered_concepts") or [] if isinstance(coverage, dict) else []
    pending = bool(state.get("research_followup_pending"))

    parts: list[str] = []
    if ratio is not None:
        parts.append(f"Coverage: {float(ratio):.0%}")
    if uncovered:
        concepts = ", ".join(str(c) for c in uncovered[:3])
        parts.append(f"gap: {concepts}")
    if pending:
        parts.append("running follow-up retrieval")
    else:
        parts.append("moving to synthesis")

    detail = " — ".join(parts) if parts else "Evaluation complete."
    return {"kind": "evaluate", "detail": detail}


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


def _build_answer_question_retrieve_payload(
    state: dict[str, Any],
) -> dict[str, Any] | None:
    chunks = _extract_answer_question_context_chunks(state)
    if not chunks:
        return None
    question = str(state.get("question") or state.get("user_input") or "").strip()
    return {
        "chunk_count": len(chunks),
        "description": _build_answer_question_retrieve_description(question),
    }


def _build_answer_question_observation_payload(
    state: dict[str, Any],
) -> dict[str, Any] | None:
    chunks = _extract_answer_question_context_chunks(state)
    if not chunks:
        return None
    question = str(state.get("question") or state.get("user_input") or "").strip()
    return {
        "kind": "observation",
        "detail": _build_answer_question_observation_detail(question, chunks),
    }


def _extract_answer_question_context_chunks(state: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question = ((state.get("tool_results") or {}).get("answer_question") or {})
    if not isinstance(answer_question, dict):
        return []
    if not answer_question.get("success", False):
        return []
    payload = answer_question.get("data")
    if not isinstance(payload, dict):
        return []
    retrieval_result = payload.get("retrieval_result")
    if not isinstance(retrieval_result, dict):
        return []
    context_chunks = retrieval_result.get("context_chunks")
    if not isinstance(context_chunks, list):
        return []
    approved_ids = {
        str(value)
        for value in payload.get("approved_chunk_ids", [])
        if str(value).strip()
    }
    if not approved_ids:
        return [chunk for chunk in context_chunks if isinstance(chunk, dict)]
    return [
        chunk
        for chunk in context_chunks
        if isinstance(chunk, dict)
        and str(chunk.get("chunk_id") or "").strip() in approved_ids
    ]


def _build_answer_question_retrieve_description(question: str) -> str:
    normalized = f" {question.lower()} "
    if _is_maintenance_interval_query(normalized):
        return "Searching maintenance interval evidence in selected document..."
    if "maintenance" in normalized:
        return "Searching maintenance evidence in selected document..."
    if _contains_any(normalized, ("procedure", "steps", "how to", "install", "replace")):
        return "Searching procedure evidence in selected document..."
    if _contains_any(
        normalized,
        ("specification", "technical data", "technical specification", "voltage", "power"),
    ):
        return "Searching technical specification evidence in selected document..."
    return "Searching grounded evidence in selected document..."


def _build_answer_question_observation_detail(
    question: str,
    chunks: list[dict[str, Any]],
) -> str:
    normalized = f" {question.lower()} "
    label = "grounded evidence"
    if _is_maintenance_interval_query(normalized):
        label = "maintenance interval evidence"
    elif "maintenance" in normalized:
        label = "maintenance evidence"
    elif _contains_any(normalized, ("procedure", "steps", "how to", "install", "replace")):
        label = "procedure evidence"
    elif _contains_any(
        normalized,
        ("specification", "technical data", "technical specification", "voltage", "power"),
    ):
        label = "technical specification evidence"

    pages = _collect_page_labels(chunks)
    if not pages:
        return f"Found {label}."
    if len(pages) == 1:
        return f"Found {label} on {pages[0]}."
    return f"Found {label} on {', '.join(pages)}."


def _collect_page_labels(chunks: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        source = chunk.get("source") or {}
        if not isinstance(source, dict):
            continue
        page_start = source.get("page_start")
        page_end = source.get("page_end")
        if page_start is None:
            continue
        if page_end is None or page_end == page_start:
            label = f"p.{page_start}"
        else:
            label = f"pp.{page_start}-{page_end}"
        if label not in labels:
            labels.append(label)
        if len(labels) >= 3:
            break
    return labels


def _is_maintenance_interval_query(question: str) -> bool:
    return _contains_any(
        question,
        (
            "maintenance interval",
            "maintenance intervals",
            "service interval",
            "inspection interval",
            "maintenance schedule",
            "preventive maintenance",
        ),
    )


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)
