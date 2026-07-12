from __future__ import annotations

from typing import Any

from src.application.agent_runtime.presenters.console.graph_result_renderer import (
    format_reference_note_line,
)


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
                "## Final Answer",
                "",
                str(data.get("answer") or result.response_text or ""),
                "",
            ]
        )
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
        lines.extend(
            [
                "## Sources Summary",
                "",
                f"- Citations: {len(data.get('citations', []) or [])}",
                f"- Context Chunks: {len(data.get('context_chunks', []) or [])}",
                "",
                "## Trace Metadata",
                "",
                f"- Route: {result.route or '-'}",
                f"- Success: {result.success}",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"
