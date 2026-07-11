from __future__ import annotations

from typing import Any


def format_retrieval_strategy(data: dict[str, Any]) -> str:
    advisor_lines = _format_strategy_advisor(data)
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
        if advisor_lines:
            lines = advisor_lines + [""] + lines
        return "\n".join(lines)

    research_plan = data.get("research_plan")
    research_trace = data.get("research_trace")
    if not isinstance(research_plan, dict):
        return "\n".join(advisor_lines).strip()
    tasks = research_plan.get("tasks")
    if not isinstance(tasks, list):
        return "\n".join(advisor_lines).strip()
    strategies_per_task = {}
    if isinstance(research_trace, dict):
        raw_map = research_trace.get("retrieval_strategies_per_task")
        if isinstance(raw_map, dict):
            strategies_per_task = raw_map
    lines: list[str] = list(advisor_lines)
    if lines:
        lines.append("")
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


def _format_strategy_advisor(data: dict[str, Any]) -> list[str]:
    advisor_result = data.get("strategy_advisor_result")
    if not isinstance(advisor_result, dict):
        return []
    status = str(advisor_result.get("status") or "").strip()
    proposal = advisor_result.get("proposal")
    advisor_reason = str(advisor_result.get("reason") or "").strip()
    trace_payload = data.get("strategy_advisor_trace")
    trace_reason = (
        str((trace_payload or {}).get("reason") or "").strip()
        if isinstance(trace_payload, dict)
        else ""
    )
    if status == "skipped":
        return []
    lines = [f"Advisor: {status or '-'}"]
    if advisor_reason:
        lines.append(f"Advisor reason: {advisor_reason}")
    elif trace_reason:
        lines.append(f"Advisor reason: {trace_reason}")
    if isinstance(proposal, dict):
        concepts = proposal.get("concepts") or []
        recommended = proposal.get("recommended_strategies") or []
        route = str(proposal.get("route") or "").strip()
        reason = str(proposal.get("reason") or "").strip()
        if concepts:
            lines.append("Concepts: " + ", ".join(str(item) for item in concepts))
        if recommended:
            lines.append(
                "Recommended: " + ", ".join(str(item) for item in recommended)
            )
        if route:
            lines.append(f"Route recommendation: {route}")
        if reason:
            lines.append(f"Advisor reason: {reason}")
    events = (((data.get("strategy_advisor_trace") or {}).get("events")) if isinstance(data.get("strategy_advisor_trace"), dict) else None) or []
    if isinstance(events, list) and events:
        lines.append(
            "Events: " + " -> ".join(
                str(event.get("name") or "").strip()
                for event in events
                if isinstance(event, dict) and str(event.get("name") or "").strip()
            )
        )
    return lines
