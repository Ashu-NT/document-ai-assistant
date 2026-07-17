from __future__ import annotations

from dataclasses import dataclass

from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerGenerationResponsePayload,
)


@dataclass(slots=True)
class PromptExecutionResult:
    parsed_output: AnswerGenerationResponsePayload
    raw_output: str
