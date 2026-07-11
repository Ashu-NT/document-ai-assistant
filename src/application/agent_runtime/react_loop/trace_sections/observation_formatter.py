from __future__ import annotations

from typing import Any

from src.application.agent_runtime.common.chunk_label_formatter import chunk_display_title
from src.application.agent_runtime.common.page_label_formatter import format_page_range_label
from src.shared.text.text_preview import preview_text


def format_observation(data: dict[str, Any], *, max_chars: int) -> str:
    context_chunks = data.get("context_chunks")
    if isinstance(context_chunks, list) and context_chunks:
        lines = ["Found evidence from the current request:"]
        for chunk in context_chunks[:4]:
            if not isinstance(chunk, dict):
                continue
            title = chunk_display_title(chunk, fallback="Evidence")
            pages = format_page_range_label(chunk.get("source"))
            detail = f"- {title}"
            if pages:
                detail += f" ({pages})"
            lines.append(detail)
        return preview_text("\n".join(lines), max_chars)
    citations = data.get("citations")
    if isinstance(citations, list) and citations:
        return preview_text(f"Collected {len(citations)} grounded citation(s).", max_chars)
    if data.get("pending_clarification"):
        question = data.get("clarification_question") or "Clarification is required."
        return preview_text(str(question), max_chars)
    return ""
