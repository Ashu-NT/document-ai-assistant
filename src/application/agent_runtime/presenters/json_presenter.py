from __future__ import annotations

from typing import Any

from src.application.agent_runtime.presenters.console.graph_result_renderer import (
    resolve_reflection_status,
)
from src.application.agent_runtime.presenters.final_answer_resolver import (
    resolve_presented_answer_text,
)


class JsonPresenter:
    def to_payload(
        self,
        *,
        session,
        result,
        react_trace,
        include_trace: bool,
    ) -> dict[str, Any]:
        data = result.data or {}
        payload = {
            "route": result.route,
            "success": result.success,
            "answer": resolve_presented_answer_text(result),
            "document_id": data.get("selected_document_id") or data.get("document_id"),
            "selected_document": session.selected_document.display_name,
            "answer_intent": data.get("answer_intent"),
            "render_provenance": data.get("render_provenance"),
            "context_chunks": data.get("context_chunks", []),
            "citations": data.get("citations", []),
            "sections": data.get("sections", []),
            "reference_notes": data.get("reference_notes", []),
            "limitation_note": data.get("limitation_note"),
            # finding F13: guardrail warnings were visible in the console
            # only, never in an exported artifact.
            "post_answer_guardrail_warnings": data.get(
                "post_answer_guardrail_warnings", []
            ),
            # finding F14: reflection visibility now goes through the same
            # extraction the console footer uses, instead of being absent
            # from this payload entirely.
            "reflection": resolve_reflection_status(result),
            "diagnostics": result.diagnostics or {},
        }
        if include_trace:
            payload["trace"] = [
                {
                    "index": step.index,
                    "event_type": step.event_type.value,
                    "title": step.title,
                    "body": step.body,
                }
                for step in getattr(react_trace, "steps", [])
            ]
        return payload

    def render(
        self,
        *,
        session,
        result,
        react_trace,
        include_trace: bool,
    ) -> dict[str, Any]:
        return self.to_payload(
            session=session,
            result=result,
            react_trace=react_trace,
            include_trace=include_trace,
        )
