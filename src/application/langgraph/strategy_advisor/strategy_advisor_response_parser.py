from __future__ import annotations

from pydantic import ValidationError

from src.application.langgraph.strategy_advisor.strategy_advisor_response_schema import (
    StrategyAdvisorResponsePayload,
)
from src.shared.exceptions import SchemaValidationError


class StrategyAdvisorResponseParser:
    def parse(self, raw_response: str) -> StrategyAdvisorResponsePayload:
        normalized = self._strip_code_fences(raw_response)
        try:
            return StrategyAdvisorResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if self._is_json_error(exc):
                raise SchemaValidationError(
                    "Malformed strategy advisor response JSON.",
                    details={"raw_response": raw_response},
                ) from exc
            raise SchemaValidationError(
                "Strategy advisor response failed schema validation.",
                details={"raw_response": raw_response, "errors": exc.errors()},
            ) from exc

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = (payload or "").strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _is_json_error(exc: ValidationError) -> bool:
        return any(error.get("type") == "json_invalid" for error in exc.errors())
