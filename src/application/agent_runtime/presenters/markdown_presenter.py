from __future__ import annotations

from typing import Any


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
