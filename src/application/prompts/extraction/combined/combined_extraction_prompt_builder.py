from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
    LegacyExtractionPromptBuilder,
)


class CombinedExtractionPromptBuilder(LegacyExtractionPromptBuilder):
    """Explicit combined extraction prompt builder for the live extraction workflow.

    The behavior intentionally stays identical to the legacy combined prompt so
    we preserve extraction output stability while making the active workflow
    dependency explicit and easier to evolve independently from compatibility
    aliases.
    """
