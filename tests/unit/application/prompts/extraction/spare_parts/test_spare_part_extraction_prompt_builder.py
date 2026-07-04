from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.spare_parts import (
    SPARE_PART_EXTRACTION_PROMPT_VERSION,
)


def test_spare_part_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SPARE_PART, context)

    assert result.prompt_version == SPARE_PART_EXTRACTION_PROMPT_VERSION
    assert '"spare_parts": [' in result.prompt_text
    assert '"part_number"' in result.prompt_text
    assert '"maintenance_tasks": [' not in result.prompt_text
