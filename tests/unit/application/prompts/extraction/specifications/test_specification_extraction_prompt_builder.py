from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.specifications import (
    SPECIFICATION_EXTRACTION_PROMPT_VERSION,
)


def test_specification_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SPECIFICATION, context)

    assert result.prompt_version == SPECIFICATION_EXTRACTION_PROMPT_VERSION
    assert '"specifications": [' in result.prompt_text
    assert '"parameter"' in result.prompt_text
    assert '"unit"' in result.prompt_text
