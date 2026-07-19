from __future__ import annotations

from typing import Any

from src.application.agent_runtime.presenters.console.graph_result_renderer import (
    format_citation_line,
    format_guardrail_warning_lines,
    format_reference_note_line,
    resolve_reflection_status,
)
from src.application.agent_runtime.presenters.final_answer_resolver import (
    resolve_presented_answer_text,
)
from src.application.langgraph.common.render_provenance import answer_heading


class MarkdownPresenter:
    def render(
        self,
        *,
        session,
        result,
        react_trace,
    ) -> str:
        data = result.data or {}
        lines = [
            "# Document AI Demo Trace",
            "",
            "## Session",
            "",
            f"- Session ID: {session.session_id}",
            f"- Started: {session.started_at}",
            f"- Selected Document: {session.selected_document.display_name or '-'}",
            f"- Mode: {result.route or '-'}",
            "",
            "## User Request",
            "",
            result.messages[-2]["content"] if len(result.messages or []) >= 2 else "-",
            "",
            "## Agent Trace",
            "",
        ]
        for step in getattr(react_trace, "steps", []):
            lines.extend(
                [
                    f"### {step.index}. {step.title}",
                    "",
                    step.body,
                    "",
                ]
            )
        lines.extend(
            [
                f"## {_answer_heading(data)}",
                "",
                str(resolve_presented_answer_text(result)),
                "",
            ]
        )
        render_provenance = data.get("render_provenance")
        if render_provenance:
            lines.extend(["## Answer From", "", str(render_provenance), ""])
        limitation_note = data.get("limitation_note")
        if limitation_note:
            lines.extend(["## Limitation", "", str(limitation_note), ""])
        sections = data.get("sections") or []
        if sections:
            lines.extend(["## Sections", ""])
            for section in sections:
                if not isinstance(section, dict):
                    continue
                lines.extend(
                    [
                        f"### {section.get('heading') or '-'}",
                        "",
                        str(section.get("body") or ""),
                        "",
                    ]
                )
        reference_notes = data.get("reference_notes") or []
        if reference_notes:
            lines.extend(["## Reference Notes", ""])
            for note in reference_notes:
                if isinstance(note, dict):
                    lines.append(f"- {format_reference_note_line(note)}")
            lines.append("")
        reflection_status = resolve_reflection_status(result)
        if reflection_status is not None:
            decision = reflection_status["decision"]
            reason = reflection_status["reason"]
            lines.extend(["## Reflection", ""])
            if decision:
                lines.append(f"- Decision: {decision}")
            if reason:
                lines.append(f"- Reason: {reason}")
            lines.append("")
        guardrail_warnings = data.get("post_answer_guardrail_warnings") or []
        if guardrail_warnings:
            # finding F13: guardrail warnings used to reach the console only,
            # never any exported artifact.
            lines.extend(["## Guardrail Notes", ""])
            for warning in guardrail_warnings:
                warning_lines = format_guardrail_warning_lines(warning)
                if not warning_lines:
                    continue
                lines.append(f"- {warning_lines[0]}")
                for violation in warning_lines[1:]:
                    lines.append(f"    - {violation}")
            lines.append("")
        citations = data.get("citations") or []
        lines.extend(["## Citations", ""])
        # finding F12: this used to be a bare `- Citations: N` count --
        # real, checkable detail (document/page/section), same source of
        # truth the console uses.
        citation_lines = [
            format_citation_line(citation) for citation in citations
        ]
        citation_lines = [line for line in citation_lines if line is not None]
        if citation_lines:
            lines.extend(f"- {line}" for line in citation_lines)
        else:
            lines.append("- None")
        lines.extend(
            [
                "",
                "## Sources Summary",
                "",
                f"- Context Chunks: {len(data.get('context_chunks', []) or [])}",
                "",
                "## Trace Metadata",
                "",
                f"- Route: {result.route or '-'}",
                f"- Success: {result.success}",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"


def _answer_heading(data: dict[str, Any]) -> str:
    return answer_heading(
        answer_intent=data.get("answer_intent"),
        render_provenance=data.get("render_provenance"),
    )
