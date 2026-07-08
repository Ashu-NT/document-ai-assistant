from __future__ import annotations

import re

from pydantic import ValidationError

from src.application.services.question_generation.question_generation_response_schema import (
    QuestionGenerationResponsePayload,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)

_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class QuestionGenerationResponseParser:
    def parse(self, response: str) -> list[str]:
        normalized = strip_code_fences_if_wrapped(
            _THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )
        try:
            payload = QuestionGenerationResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed question generation response JSON.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                "Question generation response failed schema validation.",
                details={"response": response, "errors": exc.errors()},
            ) from exc
        return payload.questions
