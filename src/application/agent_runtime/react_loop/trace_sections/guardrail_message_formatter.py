from __future__ import annotations

from typing import Any


def format_guardrail_message(data: dict[str, Any], response_text: str | None) -> str:
    reason = (
        data.get("guardrail_user_message")
        or data.get("blocked_reason")
        or response_text
    )
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    return (
        "This request was stopped by a runtime guardrail before any unsupported "
        "actions were executed."
    )
