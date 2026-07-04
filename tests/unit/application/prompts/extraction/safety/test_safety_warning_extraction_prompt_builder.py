from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.safety import (
    SAFETY_WARNING_EXTRACTION_PROMPT_VERSION,
)


def test_safety_warning_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SAFETY_WARNING, context)

    assert result.prompt_version == SAFETY_WARNING_EXTRACTION_PROMPT_VERSION
    assert '"safety_warnings": [' in result.prompt_text
    assert "danger|warning|caution|note" in result.prompt_text
