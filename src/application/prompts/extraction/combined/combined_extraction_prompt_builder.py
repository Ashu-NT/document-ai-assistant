from src.application.prompts.extraction.full.full_extraction_prompt_builder import (
    FullExtractionPromptBuilder,
)


class CombinedExtractionPromptBuilder(FullExtractionPromptBuilder):
    """Explicit combined extraction prompt builder for the live extraction workflow.

    The behavior intentionally stays identical to FullExtractionPromptBuilder so
    we preserve extraction output stability while making the active workflow
    dependency's type explicit and easier to evolve independently.
    """
