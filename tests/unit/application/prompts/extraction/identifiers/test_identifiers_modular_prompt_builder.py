from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.identifiers import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
    IdentifierExtractionPromptBuilder,
)
from src.domain.common.enums import IdentifierType


def test_identifier_builder_is_retrievable_from_the_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.IDENTIFIER, context)

    assert result.prompt_version == IDENTIFIER_EXTRACTION_PROMPT_VERSION
    assert '"identifiers": [' in result.prompt_text


def test_identifier_builder_type_guidance_is_generated_from_the_enum(sample_chunk) -> None:
    builder = IdentifierExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    for member in IdentifierType:
        assert f'"{member.value}"' in prompt


def test_identifier_builder_does_not_ask_for_full_spare_part_rows(sample_chunk) -> None:
    builder = IdentifierExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert '"spare_parts": [' not in prompt
    assert '"quantity"' not in prompt
    assert '"maintenance_tasks": [' not in prompt
    assert '"manufacturers": [' not in prompt
