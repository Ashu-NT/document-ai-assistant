import pytest

from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.common.extraction_prompt_registry import (
    get_builder,
)


@pytest.mark.parametrize("prompt_type", list(ExtractionPromptType))
def test_factory_builds_json_only_and_provenance_rules_for_every_family(
    prompt_type,
    sample_chunk,
) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id,
        chunks=[sample_chunk],
    )

    result = ExtractionPromptFactory.build(prompt_type, context)

    assert result.prompt_type == prompt_type
    assert result.prompt_version
    assert "Return JSON only." in result.prompt_text
    assert "source_chunk_id MUST be copied EXACTLY" in result.prompt_text
    assert sample_chunk.chunk_id in result.prompt_text
    assert sample_chunk.document_id in result.prompt_text


def test_factory_includes_previous_error_correction_notice(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id,
        chunks=[sample_chunk],
        previous_error="manufacturers.0: Input should be a valid dictionary",
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.MANUFACTURER, context)

    assert "Your previous response was rejected" in result.prompt_text
    assert "manufacturers.0: Input should be a valid dictionary" in result.prompt_text


def test_get_builder_raises_for_unregistered_prompt_type() -> None:
    with pytest.raises(ValueError):
        get_builder("not_a_real_prompt_type")
