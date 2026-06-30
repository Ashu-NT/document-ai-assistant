from __future__ import annotations

from typing import Any

from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.react_loop.react_step import ReactStep
from src.application.agent_runtime.react_loop.react_trace import ReactTrace


class ReactTraceBuilder:
    def build(
        self,
        *,
        user_input: str,
        result,
        policy: DemoVisibilityPolicy,
    ) -> ReactTrace:
        data = result.data or {}
        trace = ReactTrace(
            route=result.route,
            final_answer=data.get("answer") or result.response_text,
        )
        self._append(
            trace,
            ReactEvent.THOUGHT_SUMMARY,
            "Thought Summary",
            _thought_summary(result.route, data),
        )
        if result.route == "out_of_scope":
            self._append(
                trace,
                ReactEvent.GUARDRAIL,
                "Guardrail",
                _guardrail_message(data, result.response_text),
            )
            return trace
        if result.route == "blocked_action" or data.get("unsafe_request_blocked"):
            self._append(
                trace,
                ReactEvent.SAFETY_BLOCK
                if data.get("unsafe_request_blocked")
                else ReactEvent.GUARDRAIL,
                "Safety Block" if data.get("unsafe_request_blocked") else "Guardrail",
                _guardrail_message(data, result.response_text),
            )
            return trace
        if isinstance(data.get("execution_plan"), dict) and data.get("plan_steps"):
            self._append(
                trace,
                ReactEvent.PLAN,
                "Plan",
                _format_plan_steps(data.get("plan_steps")),
            )
        if policy.show_research_plan and isinstance(data.get("research_plan"), dict):
            research_body = _format_research_plan(data.get("research_plan"))
            if research_body:
                self._append(
                    trace,
                    ReactEvent.RESEARCH_PLAN,
                    "Research Plan",
                    research_body,
                )
        if policy.show_retrieval_strategy:
            retrieval_body = _format_retrieval_strategy(data)
            if retrieval_body:
                self._append(
                    trace,
                    ReactEvent.RETRIEVAL_STRATEGY,
                    "Retrieval Strategy",
                    retrieval_body,
                )
        if policy.show_tools:
            action_body = _format_action_steps(result.trace or [])
            if action_body:
                self._append(
                    trace,
                    ReactEvent.ACTION,
                    "Action",
                    action_body,
                )
        if policy.show_observations:
            observation_body = _format_observation(data, max_chars=policy.max_observation_chars)
            if observation_body:
                self._append(
                    trace,
                    ReactEvent.OBSERVATION,
                    "Observation",
                    observation_body,
                )
        if policy.show_reflection:
            reflection_body = _format_reflection(data)
            if reflection_body:
                self._append(
                    trace,
                    ReactEvent.REFLECTION,
                    "Reflection",
                    reflection_body,
                )
        if not result.success and result.response_text:
            self._append(
                trace,
                ReactEvent.ERROR,
                "Error",
                str(result.response_text).strip(),
            )
        return trace

    def _append(
        self,
        trace: ReactTrace,
        event_type: ReactEvent,
        title: str,
        body: str,
    ) -> None:
        normalized = body.strip()
        if not normalized:
            return
        trace.steps.append(
            ReactStep(
                index=len(trace.steps) + 1,
                event_type=event_type,
                title=title,
                body=normalized,
            )
        )


def _thought_summary(route: str | None, data: dict[str, Any]) -> str:
    if route == "answer_question":
        return (
            "The request asks for document evidence, so I will retrieve grounded "
            "context before answering."
        )
    if route == "planned_task":
        return (
            "The request has multiple parts, so I will execute a validated plan "
            "step by step."
        )
    if route == "deep_research":
        return (
            "The request requires synthesis across evidence groups, so I will "
            "collect task-specific evidence before writing the report."
        )
    if route == "out_of_scope":
        return (
            "This request is outside the document assistant scope, so I will not "
            "run retrieval or tools."
        )
    if route == "blocked_action" or data.get("unsafe_request_blocked"):
        if data.get("unsafe_request_blocked"):
            return (
                "The request attempts a destructive corpus operation, so I will stop "
                "before executing tools."
            )
        return (
            "The request violates a guardrail policy, so I will stop before "
            "running tools or answer generation."
        )
    if data.get("pending_clarification"):
        return "The request is ambiguous, so I need clarification before continuing."
    if route == "retrieve_evidence":
        return (
            "The request asks for supporting evidence, so I will retrieve the most "
            "relevant grounded context."
        )
    return "The request will be handled through the grounded document workflow."


def _guardrail_message(data: dict[str, Any], response_text: str | None) -> str:
    reason = (
        data.get("guardrail_user_message")
        or data.get("blocked_reason")
        or response_text
    )
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    return (
        "This request was stopped by a runtime guardrail before any unsupported "
        "actions were executed."
    )


def _format_plan_steps(plan_steps: Any) -> str:
    if not isinstance(plan_steps, list):
        return ""
    lines: list[str] = []
    for index, step in enumerate(plan_steps, start=1):
        if not isinstance(step, dict):
            continue
        description = step.get("description") or step.get("tool_name") or f"Step {index}"
        lines.append(f"{index}. {description}")
    return "\n".join(lines)


def _format_research_plan(research_plan: dict[str, Any]) -> str:
    tasks = research_plan.get("tasks")
    if not isinstance(tasks, list):
        return ""
    lines: list[str] = []
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            continue
        title = str(task.get("title") or f"Task {index}").strip()
        strategy_hint = str(task.get("strategy_hint") or "").strip()
        if strategy_hint:
            lines.append(f"{index}. {title} ({strategy_hint})")
        else:
            lines.append(f"{index}. {title}")
    return "\n".join(lines)


def _format_retrieval_strategy(data: dict[str, Any]) -> str:
    decision = data.get("retrieval_strategy_decision")
    if isinstance(decision, dict):
        primary = str(decision.get("primary_strategy") or "-")
        secondaries = decision.get("secondary_strategies") or []
        secondary_text = ", ".join(str(item) for item in secondaries) if secondaries else "-"
        lines = [
            f"Primary: {primary}",
            f"Secondary: {secondary_text}",
        ]
        confidence = decision.get("confidence")
        if isinstance(confidence, int | float):
            lines.append(f"Confidence: {float(confidence):.2f}")
        reason = str(decision.get("reason") or "").strip()
        if reason:
            lines.append(f"Reason: {reason}")
        return "\n".join(lines)

    research_plan = data.get("research_plan")
    research_trace = data.get("research_trace")
    if not isinstance(research_plan, dict):
        return ""
    tasks = research_plan.get("tasks")
    if not isinstance(tasks, list):
        return ""
    strategies_per_task = {}
    if isinstance(research_trace, dict):
        raw_map = research_trace.get("retrieval_strategies_per_task")
        if isinstance(raw_map, dict):
            strategies_per_task = raw_map
    lines: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        title = str(task.get("title") or "Task").strip()
        task_id = str(task.get("task_id") or "").strip()
        primary = (
            str(strategies_per_task.get(task_id) or "").strip()
            or str(task.get("strategy_hint") or "").strip()
        )
        if not primary:
            continue
        secondaries = _task_secondaries(task)
        lines.append(f"Task: {title}")
        lines.append(f"Primary: {primary}")
        lines.append(
            "Secondary: " + (", ".join(secondaries) if secondaries else "-")
        )
        lines.append("")
    return "\n".join(lines).strip()


def _task_secondaries(task: dict[str, Any]) -> list[str]:
    diagnostics = task.get("diagnostics")
    if isinstance(diagnostics, dict):
        raw = diagnostics.get("secondary_strategies")
        if isinstance(raw, list):
            return [str(item) for item in raw if str(item).strip()]
    title = str(task.get("title") or "").casefold()
    if "maintenance" in title or "specification" in title or "technical" in title:
        return ["TABLE_LOOKUP"]
    return []


def _format_action_steps(trace_entries: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    seen: set[tuple[str, str]] = set()
    for entry in trace_entries:
        if not isinstance(entry, dict):
            continue
        tool_name = str(entry.get("tool_name") or "").strip()
        if not tool_name:
            continue
        node_name = str(entry.get("node_name") or "").strip() or tool_name
        key = (node_name, tool_name)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"Tool: {tool_name}")
        lines.append(f"Purpose: {_tool_purpose(tool_name)}")
        lines.append("")
    return "\n".join(lines).strip()


def _tool_purpose(tool_name: str) -> str:
    purposes = {
        "retrieve_chunks": "collect document-scoped evidence.",
        "retrieve_tables": "collect structured table evidence.",
        "retrieve_identifiers": "collect identifier-level evidence.",
        "retrieve_figures": "collect figure-adjacent evidence.",
        "answer_question": "generate a grounded answer from validated evidence.",
        "find_document": "resolve the requested document in the corpus.",
        "list_documents": "list available documents in the corpus.",
    }
    return purposes.get(tool_name, "execute a validated application action.")


def _format_observation(data: dict[str, Any], *, max_chars: int) -> str:
    context_chunks = data.get("context_chunks")
    if isinstance(context_chunks, list) and context_chunks:
        lines = ["Found evidence from the current request:"]
        for chunk in context_chunks[:4]:
            if not isinstance(chunk, dict):
                continue
            title = _chunk_title(chunk)
            pages = _page_label(chunk.get("source"))
            detail = f"- {title}"
            if pages:
                detail += f" ({pages})"
            lines.append(detail)
        return _truncate("\n".join(lines), max_chars)
    citations = data.get("citations")
    if isinstance(citations, list) and citations:
        return _truncate(f"Collected {len(citations)} grounded citation(s).", max_chars)
    if data.get("pending_clarification"):
        question = data.get("clarification_question") or "Clarification is required."
        return _truncate(str(question), max_chars)
    return ""


def _format_reflection(data: dict[str, Any]) -> str:
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        return ""
    decision = (reflection_result.get("decision") or {}).get("decision") or data.get(
        "reflection_decision"
    )
    reason = (reflection_result.get("decision") or {}).get("reason")
    lines = [f"Decision: {decision or '-'}"]
    if data.get("reflection_score") is not None:
        lines.append(f"Overall score: {data.get('reflection_score')}")
    if reason:
        lines.append(f"Reason: {reason}")
    return "\n".join(lines)


def _chunk_title(chunk: dict[str, Any]) -> str:
    title = chunk.get("section_title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    section_path = chunk.get("section_path")
    if isinstance(section_path, list) and section_path:
        return str(section_path[-1])
    chunk_type = chunk.get("chunk_type")
    return str(chunk_type or "Evidence")


def _page_label(source: Any) -> str:
    if not isinstance(source, dict):
        return ""
    page_start = source.get("page_start")
    page_end = source.get("page_end")
    if page_start is None:
        return ""
    if page_end is None or page_start == page_end:
        return f"p.{page_start}"
    return f"pp.{page_start}-{page_end}"


def _truncate(value: str, limit: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."
