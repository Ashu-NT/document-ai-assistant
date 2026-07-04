from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.equipment import (
    EQUIPMENT_EXTRACTION_PROMPT_VERSION,
)


def test_equipment_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.EQUIPMENT, context)

    assert result.prompt_version == EQUIPMENT_EXTRACTION_PROMPT_VERSION
    assert '"equipment": [' in result.prompt_text
    assert '"model_number"' in result.prompt_text
    assert '"serial_number"' in result.prompt_text
