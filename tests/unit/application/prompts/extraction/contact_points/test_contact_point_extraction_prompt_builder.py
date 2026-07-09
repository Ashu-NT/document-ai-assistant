from src.application.prompts.extraction import (
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.common import ExtractionPromptContext


def test_contact_point_builder_is_retrievable_from_factory(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id,
        chunks=[sample_chunk],
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.CONTACT_POINT, context)

    assert result.prompt_type == ExtractionPromptType.CONTACT_POINT
    assert '"contact_points": [' in result.prompt_text
    assert '"owner_entity_type": "manufacturer|supplier|null"' in result.prompt_text


def test_contact_point_builder_mentions_contact_channels_and_owner_rules(
    sample_chunk,
) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id,
        chunks=[sample_chunk],
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.CONTACT_POINT, context)

    prompt = result.prompt_text.lower()
    assert "phone numbers" in prompt
    assert "email addresses" in prompt
    assert "owner_name" in prompt
    assert "owner_entity_type" in prompt
