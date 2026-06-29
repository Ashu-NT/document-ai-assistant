from __future__ import annotations

import json

from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.shared.exceptions import SchemaValidationError


class ReflectionJsonParser:
    def parse(self, payload: str) -> ReflectionDecision:
        normalized = self._strip_code_fences(payload)
        try:
            data = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise SchemaValidationError(
                "Malformed reflection response JSON.",
                details={"error": str(exc)},
            ) from exc
        if not isinstance(data, dict):
            raise SchemaValidationError(
                "Reflection response must be a JSON object.",
                details={"payload_type": type(data).__name__},
            )
        raw_decision = str(data.get("decision") or "").strip().upper()
        try:
            decision = ReflectionDecisionType(raw_decision)
        except ValueError as exc:
            raise SchemaValidationError(
                "Unknown reflection decision.",
                details={"decision": raw_decision},
            ) from exc
        missing_information = data.get("missing_information") or []
        if not isinstance(missing_information, list):
            missing_information = [str(missing_information)]
        return ReflectionDecision(
            decision=decision,
            confidence=float(data.get("confidence") or 0.0),
            reason=str(data.get("reason") or "").strip(),
            retry_query=_optional_str(data.get("retry_query")),
            clarification_question=_optional_str(data.get("clarification_question")),
            missing_information=[str(item).strip() for item in missing_information if str(item).strip()],
        )

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = (payload or "").strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                stripped = "\n".join(lines[1:-1]).strip()
        return stripped


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
