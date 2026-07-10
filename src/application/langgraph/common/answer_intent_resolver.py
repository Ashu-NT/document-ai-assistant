from __future__ import annotations

from typing import Any


def resolve_answer_intent(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    answer_intent = payload.get("answer_intent")
    if isinstance(answer_intent, str) and answer_intent:
        return answer_intent
    diagnostics = payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        value = diagnostics.get("answer_intent")
        if isinstance(value, str) and value:
            return value
    return None
