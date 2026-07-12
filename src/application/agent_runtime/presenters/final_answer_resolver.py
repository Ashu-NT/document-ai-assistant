from __future__ import annotations

from src.application.langgraph.common import (
    is_safe_failure_message,
    is_usable_reflection_decision,
    resolve_answer_text,
)


def resolve_presented_answer_text(result) -> str:
    data = result.data or {}
    answer_text = data.get("answer")
    resolved = resolve_answer_text(
        tool_results=data.get("tool_results", {}),
        fallback_response_text=result.response_text,
        reflection_decision=data.get("reflection_decision"),
        guardrail_replaced=bool(data.get("response_text_guardrail_replaced", False)),
    )
    if (
        not data.get("response_text_guardrail_replaced", False)
        and is_usable_reflection_decision(data.get("reflection_decision"))
        and is_safe_failure_message(resolved)
        and isinstance(answer_text, str)
        and answer_text.strip()
        and not is_safe_failure_message(answer_text)
    ):
        return answer_text
    if isinstance(resolved, str) and resolved.strip():
        return resolved
    return answer_text if isinstance(answer_text, str) else ""
