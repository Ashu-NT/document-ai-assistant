from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.combined import CombinedExtractionPromptBuilder
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder
from src.application.prompts.extraction.safety.safety_warning_extraction_schema import (
    SAFETY_WARNING_GUIDANCE,
)

# The compact atomicity rule added to fix the crushing-warning regression
# (PHASE 2B - SPECIALIZED SAFETYWARNING ATOMICITY FIX). Checked as a single
# marker phrase here rather than the full sentence so the test stays
# resilient to minor wording polish.
_ATOMICITY_MARKER = "never combine multiple distinct warnings"


def test_guidance_explicitly_forbids_merging_distinct_warnings() -> None:
    assert _ATOMICITY_MARKER in SAFETY_WARNING_GUIDANCE


def test_specialized_safety_warning_prompt_contains_the_atomicity_rule(
    sample_chunk,
) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.SAFETY_WARNING, context)

    assert _ATOMICITY_MARKER in result.prompt_text


def test_unrelated_specialized_prompts_do_not_gain_safety_warning_guidance(
    sample_chunk,
) -> None:
    for other_family in (
        ExtractionPromptType.SPECIFICATION,
        ExtractionPromptType.PROCEDURE,
        ExtractionPromptType.MAINTENANCE_TASK,
        ExtractionPromptType.IDENTIFIER,
    ):
        context = ExtractionPromptContext(
            document_id=sample_chunk.document_id, chunks=[sample_chunk]
        )
        result = ExtractionPromptFactory.build(other_family, context)
        assert _ATOMICITY_MARKER not in result.prompt_text, (
            f"{other_family.value} prompt unexpectedly gained SafetyWarning "
            "atomicity guidance"
        )


def test_multi_family_narrowed_path_inherits_the_rule_when_it_requests_safety_warning(
    sample_chunk,
) -> None:
    # MULTI_FAMILY's narrowed builder shares SAFETY_WARNING_GUIDANCE with the
    # specialized builder (confirmed by reading
    # extraction_narrowed_prompt_builder.py) - so this IS an intentional,
    # documented behavior change to the narrowed MULTI_FAMILY path whenever
    # narrowing selects safety_warning, not an accidental one.
    prompt = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset(
            {ExtractionPromptType.SAFETY_WARNING, ExtractionPromptType.IDENTIFIER}
        ),
    )

    assert _ATOMICITY_MARKER in prompt


def test_full_combined_multi_family_prompt_is_unaffected(sample_chunk) -> None:
    # The full/combined builder (used when narrowing is disabled or
    # resolves to every family) carries its OWN independent, hand-written
    # safety-warning guidance text - it does NOT import
    # SAFETY_WARNING_GUIDANCE - so it must NOT pick up this change. Per
    # instruction: do not touch the full MULTI_FAMILY prompt here.
    prompt = CombinedExtractionPromptBuilder().build(
        sample_chunk.document_id, [sample_chunk]
    )

    assert _ATOMICITY_MARKER not in prompt
    assert '"safety_warnings": [' in prompt
