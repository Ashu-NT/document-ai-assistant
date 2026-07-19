from __future__ import annotations

from typing import Any

from src.application.agent_runtime.common.page_label_formatter import (
    format_page_range_label,
)


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


def format_citation_line(citation: dict) -> str | None:
    """Single source of truth for "what does one citation look like as
    text" -- reused by the console block below and by MarkdownPresenter,
    so the two can no longer drift (finding F12,
    outputs/architecture/answering_and_prompt_fresh_audit.md: Markdown
    export used to reduce citations to a bare count instead of this real,
    checkable detail)."""
    if not isinstance(citation, dict):
        return None
    document_title = citation.get("document_name") or "Unknown document"
    section_path = citation.get("section_title") or "-"
    page_label = format_page_range_label(citation.get("source")) or "-"
    return f"{document_title}, {page_label} ({section_path})"


def render_citations_block(result) -> str:
    citations = (result.data or {}).get("citations") or []
    lines = ["Citations", "---------"]
    rendered_any = False
    for citation in citations:
        # finding 6.1: render real, checkable citations (document + page +
        # section), not just the bare `Sources: N` count the footer already
        # shows.
        line = format_citation_line(citation)
        if line is None:
            continue
        lines.append(f"- {line}")
        rendered_any = True
    if not rendered_any:
        return ""
    return "\n".join(lines)


def format_guardrail_warning_lines(warning: dict) -> list[str]:
    """Single source of truth for "what does one guardrail warning look
    like as text" -- the first element is the decision/reason summary, the
    rest are its individual violations, all unprefixed so each caller can
    apply its own bullet/indentation convention. Reused by the console
    block below and by MarkdownPresenter (finding F13: guardrail warnings
    previously reached console only, never any exported artifact)."""
    if not isinstance(warning, dict):
        return []
    decision = warning.get("decision") or "-"
    reason = warning.get("reason") or "-"
    lines = [f"[{decision}] {reason}"]
    lines.extend(str(violation) for violation in warning.get("violations") or [])
    return lines


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
        warning_lines = format_guardrail_warning_lines(warning)
        if not warning_lines:
            continue
        lines.append(f"- {warning_lines[0]}")
        for violation in warning_lines[1:]:
            lines.append(f"    - {violation}")
    return "\n".join(lines)
