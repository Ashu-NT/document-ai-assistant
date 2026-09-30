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
    assert "menu names, chapter numbers, parameter labels" in prompt
    assert "Omit any specification item that does not include both parameter and value." in prompt


def test_legacy_builder_uses_the_live_identifier_type_enum_not_a_hardcoded_list(
    sample_chunk,
) -> None:
    from src.domain.common.enums import IdentifierType

    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    for member in IdentifierType:
        assert f'"{member.value}"' in prompt

    stale_hardcoded_vocabulary = (
        "part_number|serial_number|model_number|certificate_number|"
        "drawing_number|component_code|manufacturer_name|supplier_name|unknown"
    )
    assert stale_hardcoded_vocabulary not in prompt


def test_legacy_builder_includes_equipment_guidance(sample_chunk) -> None:
    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "name, model_number, serial_number, and manufacturer_name are different" in prompt
    assert "not a model or serial number unless explicitly given that role" in prompt


def test_legacy_builder_includes_spare_part_tool_disambiguation_guidance(
    sample_chunk,
) -> None:
    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Tools, measuring/lifting equipment, and consumables are not SparePart" in prompt


def test_legacy_builder_includes_cross_entity_disambiguation_rules(sample_chunk) -> None:
    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Classify by ROLE, not by shape" in prompt


def test_legacy_builder_excludes_prompt_metadata_ids_from_identifier_guidance(
    sample_chunk,
) -> None:
    builder = LegacyExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Metadata labels (Document ID, Chunk ID, Section ID/Path)" in prompt
    assert "internal ids (chunk_*, doc_*, source_chunk_id) are context, not identifiers" in prompt


def test_combined_builder_preserves_legacy_prompt_output(sample_chunk) -> None:
    combined = CombinedExtractionPromptBuilder()
    legacy = LegacyExtractionPromptBuilder()

    assert combined.build(sample_chunk.document_id, [sample_chunk]) == legacy.build(
        sample_chunk.document_id,
        [sample_chunk],
    )
