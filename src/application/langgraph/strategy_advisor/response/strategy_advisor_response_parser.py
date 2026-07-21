from __future__ import annotations

from pydantic import ValidationError

from src.application.langgraph.strategy_advisor.strategy_advisor_response_schema import (
    StrategyAdvisorResponsePayload,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)


class StrategyAdvisorResponseParser:
    def parse(self, raw_response: str) -> StrategyAdvisorResponsePayload:
        normalized = strip_code_fences_if_wrapped(raw_response)
        try:
            return StrategyAdvisorResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed strategy advisor response JSON.",
                    details={"raw_response": raw_response},
                ) from exc
            raise SchemaValidationError(
                "Strategy advisor response failed schema validation.",
                details={"raw_response": raw_response, "errors": exc.errors()},
            ) from exc
