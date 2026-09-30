import re

from src.application.prompts.extraction import ExtractionPromptType
from src.application.prompts.extraction.narrowed import (
    NARROWED_EXTRACTION_PROMPT_VERSION,
    ExtractionNarrowedPromptBuilder,
)


def _extract_schema_object(prompt: str) -> str:
    match = re.search(r"Use this schema:\n(\{.*?\n\})\n", prompt, re.DOTALL)
    assert match is not None, "no schema block found in prompt"
    return match.group(1)


def test_narrowed_prompt_only_includes_requested_families(sample_chunk) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset(
            {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.IDENTIFIER}
        ),
    )

    assert builder.prompt_version == NARROWED_EXTRACTION_PROMPT_VERSION
    assert '"safety_warnings": [' in prompt
    assert '"identifiers": [' in prompt
    assert '"procedures": [' not in prompt
    assert '"spare_parts": [' not in prompt
    assert '"maintenance_tasks": [' not in prompt
    assert '"troubleshooting_entries": [' not in prompt


def test_narrowed_prompt_schema_block_joins_families_with_correct_commas(
    sample_chunk,
) -> None:
    # The schema block is illustrative pseudo-JSON (unquoted <placeholder>
    # tokens, "..." ellipsis markers) even in the original legacy prompt —
    # never meant to be strictly parsed. What actually matters here is that
    # merging multiple families' schema blocks into one object places
    # exactly one comma between each family's closing "]" and the next
    # family's key, with no missing or doubled commas at the join points
    # this builder introduces.
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset(
            {
                ExtractionPromptType.PROCEDURE,
                ExtractionPromptType.SAFETY_WARNING,
                ExtractionPromptType.IDENTIFIER,
            }
        ),
    )

    schema_text = _extract_schema_object(prompt)

    assert schema_text.startswith("{")
    assert schema_text.endswith("}")
    assert '  ],\n  "safety_warnings": [' in schema_text
    assert '  ],\n  "identifiers": [' in schema_text
    # Last family in the object must NOT have a trailing comma after its
    # closing bracket.
    assert schema_text.rstrip().endswith('  ]\n}') or schema_text.rstrip().endswith("]\n}")
    assert ",,\n" not in schema_text
    assert "]\n  \"" not in schema_text  # a join missing its comma


def test_narrowed_prompt_with_all_types_matches_legacy_family_set(sample_chunk) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset(ExtractionPromptType),
    )

    for key in (
        "maintenance_tasks",
        "spare_parts",
        "equipment",
        "manufacturers",
        "suppliers",
        "contact_points",
        "procedures",
        "specifications",
        "safety_warnings",
        "maintenance_intervals",
        "troubleshooting_entries",
        "identifiers",
    ):
        assert f'"{key}": [' in prompt


def test_narrowed_prompt_includes_guidance_and_example_for_requested_type(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )

    assert "Troubleshooting entries capture symptom/cause/remedy" in prompt
    assert "Pump fails to build pressure" in prompt  # from the worked example


def test_narrowed_prompt_includes_correction_notice_when_previous_error_given(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.IDENTIFIER}),
        previous_error="missing required field",
    )

    assert "Your previous response was rejected" in prompt
    assert "missing required field" in prompt


def test_narrowed_prompt_includes_chunk_content_and_allowed_ids(sample_chunk) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.IDENTIFIER}),
    )

    assert sample_chunk.content in prompt
    assert sample_chunk.chunk_id in prompt
    assert "Allowed chunk_id values" in prompt


def test_narrowed_identifier_prompt_uses_the_live_identifier_type_enum(sample_chunk) -> None:
    from src.domain.common.enums import IdentifierType

    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.IDENTIFIER}),
    )

    for member in IdentifierType:
        assert f'"{member.value}"' in prompt

    stale_hardcoded_vocabulary = (
        "part_number|serial_number|model_number|certificate_number|"
        "drawing_number|component_code|manufacturer_name|supplier_name|unknown"
    )
    assert stale_hardcoded_vocabulary not in prompt


def test_narrowed_prompt_includes_equipment_guidance_only_when_equipment_requested(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    with_equipment = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.EQUIPMENT}),
    )
    without_equipment = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )

    assert "name, model_number, serial_number, and manufacturer_name are different" in with_equipment
    assert (
        "name, model_number, serial_number, and manufacturer_name are different"
        not in without_equipment
    )


def test_narrowed_prompt_includes_spare_part_tool_disambiguation_only_when_requested(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    with_spare_part = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.SPARE_PART}),
    )
    without_spare_part = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )

    assert "Tools, measuring/lifting equipment, and consumables are not SparePart" in with_spare_part
    assert (
        "Tools, measuring/lifting equipment, and consumables are not SparePart"
        not in without_spare_part
    )


def test_narrowed_prompt_specification_guidance_disambiguates_from_spare_part(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.SPECIFICATION}),
    )

    assert "a parameter/value table row is not a part merely because" in prompt


def test_narrowed_prompt_includes_cross_entity_disambiguation_when_any_type_requested(
    sample_chunk,
) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )

    assert "Classify by ROLE, not by shape" in prompt


def test_narrowed_identifier_guidance_excludes_prompt_metadata_ids(sample_chunk) -> None:
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.IDENTIFIER}),
    )

    assert "Metadata labels (Document ID, Chunk ID, Section ID/Path)" in prompt
    assert "internal ids (chunk_*, doc_*, source_chunk_id) are context, not identifiers" in prompt


def test_full_and_narrowed_prompt_paths_share_identical_identifier_guidance(
    sample_chunk,
) -> None:
    from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
        LegacyExtractionPromptBuilder,
    )
    from src.application.prompts.extraction.identifiers.identifier_extraction_schema import (
        identifier_type_guidance,
    )

    narrowed = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.IDENTIFIER}),
    )
    legacy = LegacyExtractionPromptBuilder().build(sample_chunk.document_id, [sample_chunk])

    shared_guidance = identifier_type_guidance()
    assert shared_guidance in narrowed
    assert shared_guidance in legacy


def test_full_and_narrowed_prompt_paths_share_identical_equipment_guidance(
    sample_chunk,
) -> None:
    from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
        LegacyExtractionPromptBuilder,
    )
    from src.application.prompts.extraction.equipment.equipment_extraction_schema import (
        EQUIPMENT_GUIDANCE,
    )

    narrowed = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.EQUIPMENT}),
    )
    legacy = LegacyExtractionPromptBuilder().build(sample_chunk.document_id, [sample_chunk])

    assert EQUIPMENT_GUIDANCE in narrowed
    assert EQUIPMENT_GUIDANCE in legacy


def test_full_and_narrowed_prompt_paths_share_identical_spare_part_guidance(
    sample_chunk,
) -> None:
    from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
        LegacyExtractionPromptBuilder,
    )
    from src.application.prompts.extraction.spare_parts.spare_part_extraction_schema import (
        SPARE_PART_GUIDANCE,
    )

    narrowed = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.SPARE_PART}),
    )
    legacy = LegacyExtractionPromptBuilder().build(sample_chunk.document_id, [sample_chunk])

    assert SPARE_PART_GUIDANCE in narrowed
    assert SPARE_PART_GUIDANCE in legacy


def test_full_and_narrowed_prompt_paths_share_identical_specification_guidance(
    sample_chunk,
) -> None:
    from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
        LegacyExtractionPromptBuilder,
    )
    from src.application.prompts.extraction.specifications.specification_extraction_schema import (
        SPECIFICATION_GUIDANCE,
    )

    narrowed = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.SPECIFICATION}),
    )
    legacy = LegacyExtractionPromptBuilder().build(sample_chunk.document_id, [sample_chunk])

    assert SPECIFICATION_GUIDANCE in narrowed
    assert SPECIFICATION_GUIDANCE in legacy


def test_full_and_narrowed_prompt_paths_share_identical_cross_entity_rules(
    sample_chunk,
) -> None:
    from src.application.prompts.extraction.common.cross_entity_disambiguation_rules import (
        CROSS_ENTITY_DISAMBIGUATION_RULES,
    )
    from src.application.prompts.extraction.compatibility.legacy_extraction_prompt_builder import (
        LegacyExtractionPromptBuilder,
    )

    narrowed = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )
    legacy = LegacyExtractionPromptBuilder().build(sample_chunk.document_id, [sample_chunk])

    assert CROSS_ENTITY_DISAMBIGUATION_RULES in narrowed
    assert CROSS_ENTITY_DISAMBIGUATION_RULES in legacy


def test_narrowed_prompt_unrelated_types_omit_unrequested_family_guidance(
    sample_chunk,
) -> None:
    # A narrowed prompt requesting only an unrelated family should stay
    # small — it must not drag in the large EquipmentInfo/Specification/
    # SparePart guidance blocks it did not ask for (only the always-on
    # cross-entity rule block is shared unconditionally).
    builder = ExtractionNarrowedPromptBuilder()

    prompt = builder.build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset({ExtractionPromptType.TROUBLESHOOTING}),
    )

    assert "name, model_number, serial_number, and manufacturer_name are different" not in prompt
    assert "Tools, measuring/lifting equipment, and consumables are not SparePart" not in prompt
    assert "a parameter/value table row is not a part merely because" not in prompt
