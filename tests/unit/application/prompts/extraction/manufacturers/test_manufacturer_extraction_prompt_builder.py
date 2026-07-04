from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.manufacturers import (
    MANUFACTURER_EXTRACTION_PROMPT_VERSION,
)


def test_manufacturer_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.MANUFACTURER, context)

    assert result.prompt_version == MANUFACTURER_EXTRACTION_PROMPT_VERSION
    assert '"manufacturers": [' in result.prompt_text
    assert '"suppliers": [' not in result.prompt_text


def test_manufacturer_builder_distinguishes_manufacturer_from_supplier(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.MANUFACTURER, context)

    assert "supplier" in result.prompt_text.lower()
    assert "do not list it here" in result.prompt_text.lower()
