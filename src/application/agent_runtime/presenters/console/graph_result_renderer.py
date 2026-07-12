from __future__ import annotations

from typing import Any

from src.application.agent_runtime.common.page_label_formatter import (
    format_page_range_label,
)
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
    # getattr, not a direct attribute access: some lightweight result
    # doubles used elsewhere in this codebase's tests don't define
    # `diagnostics` at all (it was never read from this footer before).
    diagnostics = getattr(result, "diagnostics", None) or {}
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
        # finding 6.5: always surface reflection's stated reason next to its
        # bare decision label, not only when the fuller optional --show-react
        # trace is also requested -- the reason is what makes the decision
        # actionable rather than trivia.
        reason = _reflection_reason(data)
        # ASCII-only separator (this is a plain-text terminal renderer, and
        # the footer isn't run through console_safe_text like the rest of
        # this file's blocks are).
        fields.append(
            ("Reflection", f"{reflection} - {reason}" if reason else reflection)
        )
    elif diagnostics.get("reflection_enabled") is False:
        # reflection-off visibility follow-through: `reflection_enabled` is
        # unconditionally set in document_agent_result_builder.py's
        # diagnostics dict from state, so its being explicitly False (not
        # just absent) is a clean, already-surfaced signal that reflection
        # never ran this turn at all -- distinct from "reflection ran and
        # had nothing to add" (handled by the branch above).
        fields.append(("Reflection", "not active (self-check disabled)"))
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


def _reflection_reason(data: dict[str, Any]) -> str | None:
    reflection_result = data.get("reflection_result")
    if not isinstance(reflection_result, dict):
        return None
    decision = reflection_result.get("decision")
    if not isinstance(decision, dict):
        return None
    reason = decision.get("reason")
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    return None


def render_limitation_block(result) -> str:
    limitation_note = (result.data or {}).get("limitation_note")
    if not limitation_note:
        return ""
    # finding 6.6: give limitation_note its own clearly-labeled block right
    # after the Final Answer instead of one more `label: value` row in the
    # flat footer with no more visual weight than "Elapsed".
    return "\n".join(["Limitation", "----------", str(limitation_note)])


def render_sections_block(result) -> str:
    data = result.data or {}
    sections = data.get("sections") or []
    if not sections:
        return ""
    notes_by_id = _reference_notes_by_id(data)
    lines = ["Sections", "--------"]
    for section in sections:
        if not isinstance(section, dict):
            continue
        heading = section.get("heading")
        if heading:
            # finding 6.11: give each section heading the same short
            # underline treatment as this file's top-level blocks, scaled to
            # the heading's own length, so it doesn't visually blend into
            # the body paragraph that follows in a plain terminal.
            heading_text = str(heading)
            lines.append(heading_text)
            lines.append("-" * len(heading_text))
        if section.get("body"):
            lines.append(section["body"])
        # finding 6.2: render the reference notes this section actually
        # links to (via reference_note_ids) directly underneath it, instead
        # of leaving the section<->note relationship computed and then
        # discarded. Notes shown here are excluded from the flat Reference
        # Notes block below (see _linked_reference_note_ids) so nothing
        # prints twice.
        for note_id in section.get("reference_note_ids") or []:
            note = notes_by_id.get(note_id)
            if note is not None:
                lines.append(f"    {format_reference_note_line(note)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_reference_notes_block(result) -> str:
    data = result.data or {}
    notes = data.get("reference_notes") or []
    if not notes:
        return ""
    linked_ids = _linked_reference_note_ids(data)
    # Decision for finding 6.2: this flat block only shows notes that are
    # NOT referenced by any section's reference_note_ids -- i.e. notes
    # "orphaned" from the section breakdown (or the whole answer has no
    # sections at all, in which case every note is orphaned by definition).
    # Notes already shown grouped under their section (render_sections_block)
    # are intentionally excluded here to avoid printing the same note twice.
    orphaned = [
        note
        for note in notes
        if isinstance(note, dict) and note.get("note_id") not in linked_ids
    ]
    if not orphaned:
        return ""
    lines = ["Reference Notes", "---------------"]
    for note in orphaned:
        lines.append(format_reference_note_line(note))
    return "\n".join(lines)


def _reference_notes_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    notes = data.get("reference_notes") or []
    return {
        note["note_id"]: note
        for note in notes
        if isinstance(note, dict) and note.get("note_id")
    }


def _linked_reference_note_ids(data: dict[str, Any]) -> set[str]:
    linked: set[str] = set()
    for section in data.get("sections") or []:
        if not isinstance(section, dict):
            continue
        for note_id in section.get("reference_note_ids") or []:
            if isinstance(note_id, str):
                linked.add(note_id)
    return linked


def format_reference_note_line(note: dict[str, Any]) -> str:
    note_id = note.get("note_id") or "-"
    claim_text = note.get("claim_text") or ""
    source_number = note.get("source_number")
    source_label = f"Source {source_number}" if source_number is not None else "Source ?"
    # chunk_id itself is never printed here (it's an internal id) -- only
    # used to decide whether to flag this note as unresolved, the same
    # signal CitationGuardrail already checks internally.
    if note.get("chunk_id"):
        return f"[{note_id}] {claim_text} -> {source_label}"
    # finding 6.4: a leading, all-caps bracketed [UNVERIFIED] tag is far
    # harder to miss when skimming top-to-bottom than the old trailing
    # "(unverified)" suffix on a line that may already be 100+ characters.
    return f"[UNVERIFIED] [{note_id}] {claim_text} -> {source_label}"


def render_citations_block(result) -> str:
    citations = (result.data or {}).get("citations") or []
    lines = ["Citations", "---------"]
    rendered_any = False
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        # finding 6.1: render real, checkable citations (document + page +
        # section), not just the bare `Sources: N` count the footer already
        # shows. `source` carries page_start/page_end the same way context
        # chunks do, so reuse the existing page-range formatter instead of
        # re-deriving that logic here.
        document_title = citation.get("document_name") or "Unknown document"
        section_path = citation.get("section_title") or "-"
        page_label = format_page_range_label(citation.get("source")) or "-"
        lines.append(f"- {document_title}, {page_label} ({section_path})")
        rendered_any = True
    if not rendered_any:
        return ""
    return "\n".join(lines)


def render_guardrail_warnings_block(result) -> str:
    # finding 5.1 follow-through: post_answer_guardrail_warnings is now
    # reachable at data["post_answer_guardrail_warnings"] -- render it
    # somewhere a user/operator can actually see it, purely additive (an
    # empty list renders nothing, same as today).
    warnings = (result.data or {}).get("post_answer_guardrail_warnings") or []
    if not warnings:
        return ""
    lines = ["Guardrail Notes", "---------------"]
    for warning in warnings:
        if not isinstance(warning, dict):
            continue
        decision = warning.get("decision") or "-"
        reason = warning.get("reason") or "-"
        lines.append(f"- [{decision}] {reason}")
        for violation in warning.get("violations") or []:
            lines.append(f"    - {violation}")
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
    data = result.data or {}
    response_text = result.response_text
    answer_text = data.get("answer")
    # finding 5.5 (this renderer's own independent copy): if
    # PostResponseGuardrailService just replaced response_text with a
    # safe-fallback message (grounding failure / secret leakage / prompt
    # injection), that replacement must win outright. Without this
    # short-circuit, the recovery swap below could revert it back to the
    # raw generated answer just because the current text happens to
    # string-match one of the same sentinel messages reflection can also
    # legitimately produce -- exactly mirroring the fix already applied to
    # the canonical resolve_answer_text() in response_text_resolver.py and
    # to document_agent_result_builder.py.
    if data.get("response_text_guardrail_replaced"):
        return response_text or answer_text or ""
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
