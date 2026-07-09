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
