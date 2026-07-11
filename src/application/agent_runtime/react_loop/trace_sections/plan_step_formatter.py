from __future__ import annotations

from typing import Any


def format_plan_steps(plan_steps: Any) -> str:
    if not isinstance(plan_steps, list):
        return ""
    lines: list[str] = []
    for index, step in enumerate(plan_steps, start=1):
        if not isinstance(step, dict):
            continue
        description = step.get("description") or step.get("tool_name") or f"Step {index}"
        lines.append(f"{index}. {description}")
    return "\n".join(lines)


def format_research_plan(research_plan: dict[str, Any]) -> str:
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
