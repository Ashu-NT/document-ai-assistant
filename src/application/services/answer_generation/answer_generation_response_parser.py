from __future__ import annotations

import re

from pydantic import ValidationError

from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerGenerationResponsePayload,
)
from src.application.workflows.extraction.response.parsing.extraction_response_repairer import (
    ExtractionResponseRepairer,
)
from src.shared.exceptions import SchemaValidationError
from src.shared.llm.json_response import (
    is_json_validation_error,
    strip_code_fences_if_wrapped,
)

_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)


class AnswerGenerationResponseParser:
    """Parses the raw LLM response into AnswerGenerationResponsePayload.

    Before raising on malformed JSON, attempts the same deterministic
    JSON-repair technique already used by the extraction pipeline's
    `ExtractionResponseParser` (finding 3.1) -- trailing-comma cleanup,
    balanced-root slicing, and missing closing bracket/brace repair. This
    is a same-call rescue, not a retry: no second LLM call happens here --
    `AnswerGenerationService.generate()` owns the bounded retry-with-
    corrective-feedback loop that decides whether a second LLM call is
    warranted when this repair still isn't enough.
    """

    def __init__(self, repairer: ExtractionResponseRepairer | None = None) -> None:
        self.repairer = repairer or ExtractionResponseRepairer()

    def parse(self, response: str) -> AnswerGenerationResponsePayload:
        normalized = strip_code_fences_if_wrapped(
            _THINK_BLOCK_PATTERN.sub("", response or "").strip()
        )
        try:
            return self._validate_json_payload(normalized)
        except ValidationError as exc:
            if is_json_validation_error(exc):
                raise SchemaValidationError(
                    "Malformed answer generation response JSON.",
                    details={"response": response},
                ) from exc
            raise SchemaValidationError(
                "Answer generation response failed schema validation.",
                details={"response": response, "errors": exc.errors()},
            ) from exc

    def _validate_json_payload(
        self, normalized: str
    ) -> AnswerGenerationResponsePayload:
        try:
            return AnswerGenerationResponsePayload.model_validate_json(normalized)
        except ValidationError as exc:
            if not is_json_validation_error(exc):
                raise

            repaired = self.repairer.repair(normalized)
            if repaired is None or repaired == normalized:
                raise

            return AnswerGenerationResponsePayload.model_validate_json(repaired)
