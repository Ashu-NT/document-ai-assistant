from __future__ import annotations

from typing import Any

from src.application.guardrails.messages.guardrail_message_builder import (
    GuardrailMessageBuilder,
)
from src.application.langgraph.reflection.constants import (
    REFLECTION_SAFE_FAILURE_MESSAGE,
)

_GUARDRAIL_MESSAGE_BUILDER = GuardrailMessageBuilder()
_SAFE_FAILURE_MESSAGES = {
    REFLECTION_SAFE_FAILURE_MESSAGE.strip(),
    _GUARDRAIL_MESSAGE_BUILDER.grounding_failure_message().strip(),
}
_USABLE_REFLECTION_DECISIONS = {
    "ACCEPT",
    "ACCEPT_WITH_LIMITATIONS",
}


def resolve_answer_text(
    *,
    tool_results: dict[str, Any],
    fallback_response_text: str | None,
    reflection_decision: str | None = None,
) -> str | None:
    generated_answer = _generated_answer_text(tool_results)
    if (
        _is_usable_reflection_decision(reflection_decision)
        and _is_safe_failure_message(fallback_response_text)
        and generated_answer
        and not _is_safe_failure_message(generated_answer)
    ):
        return generated_answer

    if isinstance(fallback_response_text, str) and fallback_response_text.strip():
        return fallback_response_text

    if generated_answer:
        return generated_answer

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
        reflection_decision=_reflection_decision_from_state(state),
    )


def generated_answer_text_from_state(state: dict[str, Any]) -> str | None:
    tool_results = state.get("tool_results")
    if not isinstance(tool_results, dict):
        return None
    return _generated_answer_text(tool_results)


def is_safe_failure_message(value: str | None) -> bool:
    return _is_safe_failure_message(value)


def is_usable_reflection_decision(value: str | None) -> bool:
    return _is_usable_reflection_decision(value)


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


def _generated_answer_text(tool_results: dict[str, Any]) -> str | None:
    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if not isinstance(answer_question_payload, dict):
        return None
    for key in ("answer_text", "answer", "safe_user_message"):
        candidate = answer_question_payload.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate
    return None


def _reflection_decision_from_state(state: dict[str, Any]) -> str | None:
    value = state.get("reflection_decision")
    if isinstance(value, str) and value.strip():
        return value.strip()
    reflection_result = state.get("reflection_result")
    if isinstance(reflection_result, dict):
        decision = (reflection_result.get("decision") or {}).get("decision")
        if isinstance(decision, str) and decision.strip():
            return decision.strip()
    return None


def _is_safe_failure_message(value: str | None) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip()
    return normalized in _SAFE_FAILURE_MESSAGES


def _is_usable_reflection_decision(value: str | None) -> bool:
    if not isinstance(value, str):
        return False
    return value.strip() in _USABLE_REFLECTION_DECISIONS
