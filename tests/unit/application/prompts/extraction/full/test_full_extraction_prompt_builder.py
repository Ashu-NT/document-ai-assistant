from src.application.prompts.extraction import (
    CombinedExtractionPromptBuilder,
    IDENTIFIER_EXTRACTION_PROMPT_VERSION,
)
from src.application.prompts.extraction.full.full_extraction_prompt_builder import (
    FullExtractionPromptBuilder,
)


def test_full_builder_still_returns_a_combined_prompt_string(sample_chunk) -> None:
    builder = FullExtractionPromptBuilder()

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


def test_full_builder_uses_the_live_identifier_type_enum_not_a_hardcoded_list(
    sample_chunk,
) -> None:
    from src.domain.common.enums import IdentifierType

    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    for member in IdentifierType:
        assert f'"{member.value}"' in prompt

    stale_hardcoded_vocabulary = (
        "part_number|serial_number|model_number|certificate_number|"
        "drawing_number|component_code|manufacturer_name|supplier_name|unknown"
    )
    assert stale_hardcoded_vocabulary not in prompt


def test_full_builder_includes_equipment_guidance(sample_chunk) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "name, model_number, serial_number, and manufacturer_name are different" in prompt
    assert "not a model or serial number unless explicitly given that role" in prompt


def test_full_builder_includes_spare_part_tool_disambiguation_guidance(
    sample_chunk,
) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Tools, measuring/lifting equipment, and consumables are not SparePart" in prompt


def test_full_builder_includes_cross_entity_disambiguation_rules(sample_chunk) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Classify by ROLE, not by shape" in prompt


def test_full_builder_excludes_prompt_metadata_ids_from_identifier_guidance(
    sample_chunk,
) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Metadata labels (Document ID, Chunk ID, Section ID/Path)" in prompt
    assert "internal ids (chunk_*, doc_*, source_chunk_id) are context, not identifiers" in prompt


def test_combined_builder_preserves_full_prompt_output(sample_chunk) -> None:
    combined = CombinedExtractionPromptBuilder()
    full = FullExtractionPromptBuilder()

    assert combined.build(sample_chunk.document_id, [sample_chunk]) == full.build(
        sample_chunk.document_id,
        [sample_chunk],
    )


def _clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def test_full_builder_includes_source_text_and_instructions(sample_chunk) -> None:
    second_chunk = _clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="The spare part number is HP-001 and the manufacturer is Example Manufacturer.",
    )
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk, second_chunk],
    )

    assert builder.prompt_version == IDENTIFIER_EXTRACTION_PROMPT_VERSION
    assert sample_chunk.document_id in prompt
    assert sample_chunk.chunk_id in prompt
    assert second_chunk.chunk_id in prompt
    assert sample_chunk.content in prompt
    assert second_chunk.content in prompt
    assert "Maintenance Schedule" in prompt
    assert '"maintenance_tasks": [' in prompt
    assert '"spare_parts": [' in prompt
    assert '"equipment": [' in prompt
    assert '"manufacturers": [' in prompt
    assert '"suppliers": [' in prompt
    assert '"procedures": [' in prompt
    assert '"specifications": [' in prompt
    assert '"safety_warnings": [' in prompt
    assert '"maintenance_intervals": [' in prompt
    assert '"troubleshooting_entries": [' in prompt
    assert '"identifiers": [' in prompt
    assert "Return JSON only." in prompt
    assert "Allowed chunk_id values" in prompt
    assert f"{sample_chunk.chunk_id}, {second_chunk.chunk_id}" in prompt
    assert "Never write [null]" in prompt


def test_full_builder_omits_correction_notice_by_default(sample_chunk) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(sample_chunk.document_id, [sample_chunk])

    assert "Your previous response was rejected" not in prompt


def test_full_builder_includes_previous_error_when_retrying(sample_chunk) -> None:
    builder = FullExtractionPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        previous_error="spare_parts.0: Input should be a valid dictionary",
    )

    assert "Your previous response was rejected" in prompt
    assert "spare_parts.0: Input should be a valid dictionary" in prompt
    assert prompt.index("Your previous response was rejected") < prompt.index(
        "You extract structured information"
    )
