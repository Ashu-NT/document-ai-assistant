from __future__ import annotations

from typing import Any


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
            "answer": data.get("answer") or result.response_text,
            "document_id": data.get("selected_document_id") or data.get("document_id"),
            "selected_document": session.selected_document.display_name,
            "context_chunks": data.get("context_chunks", []),
            "citations": data.get("citations", []),
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
