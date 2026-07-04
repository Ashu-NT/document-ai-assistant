from __future__ import annotations

from src.application.prompts.extraction.common.extraction_prompt_context import (
    ExtractionPromptContext,
)
from src.application.prompts.extraction.common.extraction_prompt_registry import (
    get_builder,
)
from src.application.prompts.extraction.common.extraction_prompt_result import (
    ExtractionPromptResult,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)


class ExtractionPromptFactory:
    @staticmethod
    def build(
        prompt_type: ExtractionPromptType,
        context: ExtractionPromptContext,
    ) -> ExtractionPromptResult:
        builder = get_builder(prompt_type)
        prompt_text = builder.build(
            context.document_id,
            context.chunks,
            previous_error=context.previous_error,
        )
        return ExtractionPromptResult(
            prompt_type=prompt_type,
            prompt_text=prompt_text,
            prompt_version=builder.prompt_version,
        )
