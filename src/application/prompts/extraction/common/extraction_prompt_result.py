from __future__ import annotations

from dataclasses import dataclass

from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)


@dataclass(frozen=True, slots=True)
class ExtractionPromptResult:
    prompt_type: ExtractionPromptType
    prompt_text: str
    prompt_version: str
