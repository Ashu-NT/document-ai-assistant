from __future__ import annotations

from typing import Any


def resolve_answer_text(
    *,
    tool_results: dict[str, Any],
    fallback_response_text: str | None,
) -> str | None:
    format_combined_payload = tool_results.get("format_combined_answer")
    if (
        fallback_response_text
        and isinstance(format_combined_payload, dict)
        and format_combined_payload.get("success", False)
    ):
        return fallback_response_text

    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        candidate = (
            answer_question_payload.get("answer_text")
            or answer_question_payload.get("safe_user_message")
        )
        if isinstance(candidate, str) and candidate.strip():
            return candidate

    return fallback_response_text


def resolve_state_response_text(state: dict[str, Any]) -> str | None:
    tool_results = state.get("tool_results")
    if not isinstance(tool_results, dict):
        tool_results = {}
    fallback_response_text = state.get("response_text")
    if not isinstance(fallback_response_text, str):
        fallback_response_text = None
    return resolve_answer_text(
        tool_results=tool_results,
        fallback_response_text=fallback_response_text,
    )


def _tool_payload(
    tool_results: dict[str, Any],
    tool_name: str,
) -> Any | None:
    tool_result = tool_results.get(tool_name)
    if not isinstance(tool_result, dict):
        return None
    if not tool_result.get("success", False):
        return None
    return tool_result.get("data")
