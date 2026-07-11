from __future__ import annotations

from typing import Any

from src.application.langgraph.common import (
    is_safe_failure_message,
    is_usable_reflection_decision,
    reflection_decision_from_state,
)
from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.shared.text.text_preview import console_safe_text


def render_graph_result(
    *,
    user_input: str,
    result,
    react_trace: ReactTrace | None,
    session,
    policy: DemoVisibilityPolicy,
    show_react: bool,
    react_presenter: ReactPresenter,
) -> str:
    lines = [
        "User Request",
        "------------",
        console_safe_text(user_input),
        "",
    ]
    if show_react and react_trace is not None:
        trace_text = react_presenter.render(react_trace, policy=policy)
        if trace_text:
            lines.extend([trace_text, ""])
    lines.extend(
        [
            "Final Answer",
            "------------",
            console_safe_text(_final_answer_text(result)),
            "",
        ]
    )
    sections_block = _render_sections_block(result)
    if sections_block:
        lines.extend([console_safe_text(sections_block), ""])
    reference_notes_block = _render_reference_notes_block(result)
    if reference_notes_block:
        lines.extend([console_safe_text(reference_notes_block), ""])
    footer = _render_status_footer(result, session=session)
    if footer:
        lines.append(footer)
    return "\n".join(line for line in lines if line is not None).rstrip()


def _render_status_footer(result, *, session) -> str:
    data = result.data or {}
    fields = []
    if session.selected_document.display_name:
        fields.append(("Document", session.selected_document.display_name))
    if result.route:
        fields.append(("Route", result.route))
        fields.append(("Mode", _route_mode_label(result.route)))
    strategy = _strategy_label(data)
    if strategy:
        fields.append(("Strategy", strategy))
    reflection = data.get("reflection_decision") or reflection_decision_from_state(data)
    if reflection:
        fields.append(("Reflection", reflection))
    limitation_note = data.get("limitation_note")
    if limitation_note:
        fields.append(("Limitation", limitation_note))
    source_count = len(data.get("citations", []) or [])
    if source_count:
        fields.append(("Sources", source_count))
    elapsed_seconds = _elapsed_seconds(result.trace or [])
    if elapsed_seconds is not None:
        fields.append(("Elapsed", f"{elapsed_seconds:.1f} s"))
    if not fields:
        return ""
    lines = ["--------------------------------------------------"]
    for label, value in fields:
        if value in {None, ""}:
            continue
        lines.append(f"{label:<11}: {value}")
    lines.append("--------------------------------------------------")
    return "\n".join(lines)


def _render_sections_block(result) -> str:
    sections = (result.data or {}).get("sections") or []
    if not sections:
        return ""
    lines = ["Sections", "--------"]
    for section in sections:
        if not isinstance(section, dict):
            continue
        if section.get("heading"):
            lines.append(section["heading"])
        if section.get("body"):
            lines.append(section["body"])
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_reference_notes_block(result) -> str:
    notes = (result.data or {}).get("reference_notes") or []
    if not notes:
        return ""
    lines = ["Reference Notes", "---------------"]
    for note in notes:
        if not isinstance(note, dict):
            continue
        note_id = note.get("note_id") or "-"
        claim_text = note.get("claim_text") or ""
        source_number = note.get("source_number")
        source_label = f"Source {source_number}" if source_number is not None else "Source ?"
        # chunk_id itself is never printed here (it's an internal id) --
        # only used to decide whether to flag this note as unresolved, the
        # same signal CitationGuardrail already checks internally.
        marker = "" if note.get("chunk_id") else " (unverified)"
        lines.append(f"[{note_id}] {claim_text} -> {source_label}{marker}")
    return "\n".join(lines)


def _route_mode_label(route: str) -> str:
    mapping = {
        "deep_research": "Deep Research",
        "planned_task": "Planned Task",
        "answer_question": "Question Answering",
        "retrieve_evidence": "Evidence Retrieval",
        "out_of_scope": "Scope Redirect",
        "blocked_action": "Safety Block",
    }
    return mapping.get(route, route.replace("_", " ").title())


def _strategy_label(data: dict[str, Any]) -> str | None:
    decision = data.get("retrieval_strategy_decision")
    if isinstance(decision, dict):
        primary = decision.get("primary_strategy")
        secondaries = decision.get("secondary_strategies") or []
        if primary and secondaries:
            return f"{primary} + {', '.join(str(item) for item in secondaries)}"
        if primary:
            return str(primary)
    research_plan = data.get("research_plan")
    if isinstance(research_plan, dict):
        tasks = research_plan.get("tasks") or []
        hints = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            hint = task.get("strategy_hint")
            if isinstance(hint, str) and hint not in hints:
                hints.append(hint)
        if hints:
            return " + ".join(hints[:2])
    return None


def _final_answer_text(result) -> str:
    data = result.data or {}
    response_text = result.response_text
    answer_text = data.get("answer")
    reflection = data.get("reflection_decision") or reflection_decision_from_state(data)
    if (
        is_usable_reflection_decision(reflection)
        and is_safe_failure_message(response_text)
        and isinstance(answer_text, str)
        and answer_text.strip()
        and not is_safe_failure_message(answer_text)
    ):
        return answer_text
    return response_text or answer_text or ""


def _elapsed_seconds(trace_entries: list[dict[str, Any]]) -> float | None:
    if not trace_entries:
        return None
    total_ms = 0.0
    for entry in trace_entries:
        if not isinstance(entry, dict):
            continue
        elapsed = entry.get("elapsed_ms")
        if isinstance(elapsed, int | float):
            total_ms += float(elapsed)
    if total_ms <= 0:
        return None
    return total_ms / 1000.0
