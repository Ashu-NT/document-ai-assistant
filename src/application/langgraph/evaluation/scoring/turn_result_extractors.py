from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphResult
from src.application.langgraph.common.value_coercion import optional_str
from src.application.langgraph.evaluation.scoring.eval_value_helpers import (
    unique_preserving_order,
)
from src.application.langgraph.routing import RouteType


def extract_trace_tool_names(trace: list[dict[str, Any]]) -> list[str]:
    return unique_preserving_order(
        str(entry.get("tool_name"))
        for entry in trace
        if isinstance(entry, dict) and entry.get("tool_name")
    )


def extract_plan_tool_names(data: dict[str, Any]) -> list[str]:
    validated_plan = data.get("validated_plan")
    if isinstance(validated_plan, dict):
        steps = validated_plan.get("steps")
        if isinstance(steps, list):
            return unique_preserving_order(
                str(step.get("tool_name"))
                for step in steps
                if isinstance(step, dict) and step.get("tool_name")
            )

    plan_steps = data.get("plan_steps")
    if isinstance(plan_steps, list):
        return unique_preserving_order(
            str(step.get("tool_name"))
            for step in plan_steps
            if isinstance(step, dict) and step.get("tool_name")
        )
    return []


def extract_context_document_ids(data: dict[str, Any]) -> list[str]:
    context_chunks = data.get("context_chunks")
    if not isinstance(context_chunks, list):
        return []
    return unique_preserving_order(
        str(chunk.get("document_id"))
        for chunk in context_chunks
        if isinstance(chunk, dict) and chunk.get("document_id")
    )


def extract_turn_errors(result: GraphResult) -> list[str]:
    errors: list[str] = []
    if result.error_code:
        errors.append(result.error_code)
    diagnostics = result.diagnostics or {}
    if isinstance(diagnostics.get("planning_errors"), list):
        errors.extend(
            str(item)
            for item in diagnostics["planning_errors"]
            if isinstance(item, str) and item
        )
    data = result.data or {}
    if isinstance(data.get("planning_errors"), list):
        errors.extend(
            str(item)
            for item in data["planning_errors"]
            if isinstance(item, str) and item
        )
    return unique_preserving_order(errors)


def research_plan_task_count(value: Any) -> int:
    if not isinstance(value, dict):
        return 0
    tasks = value.get("tasks")
    if not isinstance(tasks, list):
        return 0
    return sum(1 for task in tasks if isinstance(task, dict))


def research_report_section_count(value: Any) -> int:
    if not isinstance(value, dict):
        return 0
    sections = value.get("sections")
    if not isinstance(sections, list):
        return 0
    return sum(1 for section in sections if isinstance(section, dict))


def research_task_counts(value: Any) -> tuple[int, int]:
    if not isinstance(value, list):
        return 0, 0
    task_count = 0
    success_count = 0
    for item in value:
        if not isinstance(item, dict):
            continue
        task_count += 1
        if bool(item.get("success")):
            success_count += 1
    return task_count, success_count


def resolve_unsafe_blocked_flag(*, result: GraphResult) -> bool:
    data = result.data or {}
    diagnostics = result.diagnostics or {}
    return bool(
        result.route == RouteType.BLOCKED_ACTION.value
        or data.get("unsafe_request_blocked")
        or diagnostics.get("unsafe_request_blocked")
    )


def resolve_blocked_reason(*, result: GraphResult) -> str | None:
    data = result.data or {}
    diagnostics = result.diagnostics or {}
    return optional_str(data.get("blocked_reason")) or optional_str(
        diagnostics.get("blocked_reason")
    )


def resolve_blocked_terms(*, result: GraphResult) -> list[str]:
    data = result.data or {}
    diagnostics = result.diagnostics or {}
    candidates = data.get("blocked_terms")
    if not isinstance(candidates, list):
        candidates = diagnostics.get("blocked_terms")
    if not isinstance(candidates, list):
        return []
    return [str(item) for item in candidates if isinstance(item, str) and item]
