from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
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
    assert '"procedures": [' in prompt
    assert '"procedure_type": "<one of:' in prompt
    assert '"specifications": [' in prompt
    assert '"safety_warnings": [' in prompt
    assert '"maintenance_intervals": [' in prompt
    assert '"troubleshooting_entries": [' in prompt
    assert '"identifiers": [' in prompt
    assert "Only emit an array item when the required evidence fields for that entity are present." in prompt
    assert "For identifiers: if raw_value is missing, omit the item instead of returning only identifier_type." in prompt
    assert "For specifications: omit any item that does not include both parameter and value." in prompt


def test_combined_builder_preserves_legacy_prompt_output(sample_chunk) -> None:
    combined = CombinedExtractionPromptBuilder()
    legacy = LegacyExtractionPromptBuilder()

    assert combined.build(sample_chunk.document_id, [sample_chunk]) == legacy.build(
        sample_chunk.document_id,
        [sample_chunk],
    )
