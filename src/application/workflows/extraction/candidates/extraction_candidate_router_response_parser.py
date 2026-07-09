from __future__ import annotations

import re

from pydantic import ValidationError

from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)
from src.application.workflows.extraction.candidates.extraction_candidate_router_schema import (
    ExtractionCandidateRouterPayload,
)

_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class ExtractionCandidateRouterResponseParser:
    def parse(self, response: str) -> ExtractionCandidateRouterPayload:
        normalized = strip_code_fences_if_wrapped(
            _THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )
        try:
            return ExtractionCandidateRouterPayload.model_validate_json(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed extraction candidate router response.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                "Extraction candidate router response failed schema validation.",
                details={"response": response, "errors": exc.errors()},
            ) from exc
