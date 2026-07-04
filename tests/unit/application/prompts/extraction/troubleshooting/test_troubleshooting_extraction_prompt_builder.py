from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.troubleshooting import (
    TROUBLESHOOTING_EXTRACTION_PROMPT_VERSION,
)


def test_troubleshooting_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.TROUBLESHOOTING, context)

    assert result.prompt_version == TROUBLESHOOTING_EXTRACTION_PROMPT_VERSION
    assert '"troubleshooting_entries": [' in result.prompt_text
    assert "symptom" in result.prompt_text
