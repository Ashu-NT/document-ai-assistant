from __future__ import annotations

import re

from pydantic import ValidationError

from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerGenerationResponsePayload,
)
from src.shared.exceptions import SchemaValidationError

_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class AnswerGenerationResponseParser:
    def parse(self, response: str) -> AnswerGenerationResponsePayload:
        normalized = self._strip_code_fences(
            _THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )
        try:
            return AnswerGenerationResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if self._is_json_error(exc):
                raise SchemaValidationError(
                    "Malformed answer generation response JSON.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                "Answer generation response failed schema validation.",
                details={"response": response, "errors": exc.errors()},
            ) from exc

    @staticmethod
    def _strip_code_fences(payload: str) -> str:
        stripped = payload.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _is_json_error(exc: ValidationError) -> bool:
        return any(error.get("type") == "json_invalid" for error in exc.errors())
