from __future__ import annotations

from src.application.langgraph.reflection.models import (
    ReflectionDecision,
)
from src.application.langgraph.reflection.services.reflection_response_schema import (
    ReflectionResponsePayload,
)
from pydantic import ValidationError
from src.shared.exceptions import SchemaValidationError


class ReflectionJsonParser:
    def parse(self, payload: str) -> ReflectionDecision:
        normalized = self._strip_code_fences(payload)
        try:
            data = ReflectionResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if self._is_json_error(exc):
                raise SchemaValidationError(
                    "Malformed reflection response JSON.",
                    details={"payload": payload},
                ) from exc
            raise SchemaValidationError(
                "Reflection response failed schema validation.",
                details={"payload": payload, "errors": exc.errors()},
            ) from exc
        return ReflectionDecision(
            decision=data.decision,
            confidence=data.confidence,
            reason=data.reason,
            retry_query=data.retry_query,
            clarification_question=data.clarification_question,
            missing_information=list(data.missing_information),
        )

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = (payload or "").strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                stripped = "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _is_json_error(exc: ValidationError) -> bool:
        return any(error.get("type") == "json_invalid" for error in exc.errors())
