from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.suppliers import (
    SUPPLIER_EXTRACTION_PROMPT_VERSION,
)


def test_supplier_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SUPPLIER, context)

    assert result.prompt_version == SUPPLIER_EXTRACTION_PROMPT_VERSION
    assert '"suppliers": [' in result.prompt_text
    assert '"manufacturers": [' not in result.prompt_text


def test_supplier_builder_distinguishes_supplier_from_manufacturer(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SUPPLIER, context)

    assert "manufacturer" in result.prompt_text.lower()
    assert "do not list it here" in result.prompt_text.lower()
