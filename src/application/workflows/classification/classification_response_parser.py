import re
from pydantic import ValidationError

from src.application.workflows.classification.classification_response_schema import (
    ClassificationResponsePayload,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)

THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class ClassificationResponseParser:
    def parse(self, response: str) -> ClassificationResponsePayload:
        normalized = strip_code_fences_if_wrapped(
            THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )
        try:
            return ClassificationResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed classification response.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                "Classification response failed schema validation.",
                details={"response": response, "errors": exc.errors()},
            ) from exc
