from __future__ import annotations

from typing import Any

from src.application.agent_runtime.policies.demo_visibility_policy import (
    DemoVisibilityPolicy,
)
from src.application.agent_runtime.presenters.console.graph_result_blocks import (
    format_citation_line,
    format_guardrail_warning_lines,
    format_reference_note_line,
    render_citations_block,
    render_guardrail_warnings_block,
    render_limitation_block,
    render_reference_notes_block,
    render_sections_block,
)
from src.application.agent_runtime.presenters.console.graph_result_reflection_status import (
    resolve_reflection_status,
)
from src.application.agent_runtime.presenters.final_answer_resolver import (
    resolve_presented_answer_text,
)
from src.application.langgraph.common.render_provenance import answer_heading
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.shared.text.text_preview import console_safe_text

# Re-exported for backward compatibility: every other presenter/CLI in this
# codebase imports these names from this module specifically, so moving
# their bodies into graph_result_blocks.py / graph_result_reflection_status.py
# (to keep this file under the 300-LOC convention) stays invisible to callers.
__all__ = [
    "render_graph_result",
    "format_citation_line",
    "format_guardrail_warning_lines",
    "format_reference_note_line",
    "render_citations_block",
    "render_guardrail_warnings_block",
    "render_limitation_block",
    "render_reference_notes_block",
    "render_sections_block",
    "resolve_reflection_status",
    "final_answer_text",
]


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
    answer_block_heading = _answer_block_heading(result)
    lines.extend(
        [
            answer_block_heading,
            "-" * len(answer_block_heading),
            console_safe_text(final_answer_text(result)),
            "",
        ]
    )
    # finding 6.3: when `sections` is also populated below, its content may
    # overlap with this flat answer_text block. That is a deliberate
    # consequence of the schema allowing both fields together -- answer_text
    # is always the safe, always-populated summary, while sections is the
    # optional additive structured breakdown (see AnswerGenerationResponsePayload's
    # own docstring) -- not a duplication bug to silently hide. Removing
    # either risks losing real answer content that the other doesn't carry,
    # so both render; this comment documents the judgment call for anyone
    # revisiting it later.
    limitation_block = render_limitation_block(result)
    if limitation_block:
        lines.extend([console_safe_text(limitation_block), ""])
    sections_block = render_sections_block(result)
    if sections_block:
        lines.extend([console_safe_text(sections_block), ""])
    reference_notes_block = render_reference_notes_block(result)
    if reference_notes_block:
        lines.extend([console_safe_text(reference_notes_block), ""])
    citations_block = render_citations_block(result)
    if citations_block:
        lines.extend([console_safe_text(citations_block), ""])
    guardrail_block = render_guardrail_warnings_block(result)
    if guardrail_block:
        lines.extend([console_safe_text(guardrail_block), ""])
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
    render_provenance = data.get("render_provenance")
    if render_provenance:
        fields.append(("Answer From", render_provenance))
    reflection_status = resolve_reflection_status(result)
    if reflection_status is not None:
        decision = reflection_status["decision"]
        reason = reflection_status["reason"]
        # finding 6.5: always surface reflection's stated reason next to its
        # bare decision label, not only when the fuller optional --show-react
        # trace is also requested -- the reason is what makes the decision
        # actionable rather than trivia. ASCII-only separator (this is a
        # plain-text terminal renderer, and the footer isn't run through
        # console_safe_text like the rest of this file's blocks are).
        fields.append(
            (
                "Reflection",
                f"{decision} - {reason}" if decision and reason else (decision or reason),
            )
        )
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


def final_answer_text(result) -> str:
    return resolve_presented_answer_text(result)


def _answer_block_heading(result) -> str:
    data = result.data or {}
    return answer_heading(
        answer_intent=data.get("answer_intent"),
        render_provenance=data.get("render_provenance"),
    )


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
