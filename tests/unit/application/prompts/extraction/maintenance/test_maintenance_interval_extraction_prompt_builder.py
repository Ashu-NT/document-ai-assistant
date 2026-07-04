from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.maintenance import (
    MAINTENANCE_INTERVAL_EXTRACTION_PROMPT_VERSION,
)


def test_maintenance_interval_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(
        ExtractionPromptType.MAINTENANCE_INTERVAL, context
    )

    assert result.prompt_version == MAINTENANCE_INTERVAL_EXTRACTION_PROMPT_VERSION
    assert '"maintenance_intervals": [' in result.prompt_text
    assert '"maintenance_tasks": [' not in result.prompt_text
