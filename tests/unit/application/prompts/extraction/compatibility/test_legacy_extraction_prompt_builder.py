from src.application.prompts.extraction import (
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
    IdentifierExtractionPromptBuilder,
)
from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
    LegacyExtractionPromptBuilder,
)


def test_package_root_reexports_legacy_builder_for_backward_compatibility() -> None:
    assert IdentifierExtractionPromptBuilder is LegacyExtractionPromptBuilder


def test_legacy_builder_still_returns_a_combined_prompt_string(sample_chunk) -> None:
    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert isinstance(prompt, str)
    assert builder.prompt_version == IDENTIFIER_EXTRACTION_PROMPT_VERSION
    assert '"maintenance_tasks": [' in prompt
    assert '"spare_parts": [' in prompt
    assert '"equipment": [' in prompt
    assert '"manufacturers": [' in prompt
    assert '"suppliers": [' in prompt
    assert '"identifiers": [' in prompt
