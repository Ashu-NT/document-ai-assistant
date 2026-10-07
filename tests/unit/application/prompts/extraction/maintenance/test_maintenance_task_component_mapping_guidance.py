from src.application.prompts.extraction import (
    ExtractionPromptContext,
    ExtractionPromptFactory,
    ExtractionPromptType,
)
from src.application.prompts.extraction.combined import CombinedExtractionPromptBuilder
from src.application.prompts.extraction.maintenance.maintenance_task_extraction_schema import (
    MAINTENANCE_TASK_GUIDANCE,
)
from src.application.prompts.extraction.narrowed import ExtractionNarrowedPromptBuilder

# PHASE 2B MAINTENANCETASK STRUCTURED TABLE FIELD-MAPPING EXPERIMENT. Checked
# as marker phrases (not the full sentence) so the test stays resilient to
# minor wording polish.
_PREFER_EXPLICIT_MARKER = "prefer it over"
_NO_INVENTION_MARKER = "do not invent component_name"

# Values this experiment's own investigation used for reporting - must never
# leak into production guidance (see task section 2).
_MTU_SPECIFIC_VALUES = (
    "ENGINE OPERATIONAL MONITORING",
    "WM00285",
    "WM00286",
    "Check engine oil level",
    "Visually inspect engine for leaks and general condition",
)


def test_guidance_describes_component_name_semantics() -> None:
    lowered = MAINTENANCE_TASK_GUIDANCE.lower()
    assert "component_name" in lowered
    assert "component" in lowered or "equipment" in lowered or "item" in lowered


def test_guidance_prefers_explicit_structured_evidence_over_inference() -> None:
    assert _PREFER_EXPLICIT_MARKER in MAINTENANCE_TASK_GUIDANCE


def test_guidance_does_not_require_inventing_a_missing_component() -> None:
    assert _NO_INVENTION_MARKER in MAINTENANCE_TASK_GUIDANCE.lower()


def test_guidance_contains_no_mtu_specific_values() -> None:
    for value in _MTU_SPECIFIC_VALUES:
        assert value not in MAINTENANCE_TASK_GUIDANCE, (
            f"production guidance must generalize - found MTU-specific value {value!r}"
        )


def test_guidance_does_not_hardcode_a_column_name_dictionary() -> None:
    # The rule must be semantic, not a hardcoded list of column header
    # synonyms to match against - a handful of illustrative nouns in one
    # sentence is fine, a structured dict/enum-like list would not be.
    assert "elif" not in MAINTENANCE_TASK_GUIDANCE
    assert MAINTENANCE_TASK_GUIDANCE.count("\n") <= 2


def test_specialized_maintenance_task_prompt_contains_the_guidance(sample_chunk) -> None:
    context = ExtractionPromptContext(
        document_id=sample_chunk.document_id, chunks=[sample_chunk]
    )

    result = ExtractionPromptFactory.build(ExtractionPromptType.MAINTENANCE_TASK, context)

    assert MAINTENANCE_TASK_GUIDANCE in result.prompt_text


def test_unrelated_specialized_prompts_do_not_gain_maintenance_task_guidance(
    sample_chunk,
) -> None:
    for other_family in (
        ExtractionPromptType.SPECIFICATION,
        ExtractionPromptType.PROCEDURE,
        ExtractionPromptType.SAFETY_WARNING,
        ExtractionPromptType.SPARE_PART,
    ):
        context = ExtractionPromptContext(
            document_id=sample_chunk.document_id, chunks=[sample_chunk]
        )
        result = ExtractionPromptFactory.build(other_family, context)
        assert MAINTENANCE_TASK_GUIDANCE not in result.prompt_text, (
            f"{other_family.value} prompt unexpectedly gained MaintenanceTask guidance"
        )


def test_prompt_size_increase_from_the_guidance_is_minimal() -> None:
    # Reported, not just asserted: this is the exact per-call character
    # overhead the new guidance adds to every specialized MaintenanceTask
    # call (and to MULTI_FAMILY's narrowed path whenever it requests
    # MaintenanceTask).
    assert len(MAINTENANCE_TASK_GUIDANCE) < 400


def test_multi_family_narrowed_path_inherits_the_rule_when_it_requests_maintenance_task(
    sample_chunk,
) -> None:
    # MULTI_FAMILY's narrowed builder shares MAINTENANCE_TASK_GUIDANCE with
    # the specialized builder via _FAMILY_GUIDANCE (same precedent as
    # SAFETY_WARNING_GUIDANCE) - an intentional, documented behavior change
    # to the narrowed MULTI_FAMILY path whenever narrowing selects
    # maintenance_task, not an accidental one.
    prompt = ExtractionNarrowedPromptBuilder().build(
        sample_chunk.document_id,
        [sample_chunk],
        requested_types=frozenset(
            {ExtractionPromptType.MAINTENANCE_TASK, ExtractionPromptType.IDENTIFIER}
        ),
    )

    assert MAINTENANCE_TASK_GUIDANCE in prompt


def test_full_combined_multi_family_prompt_is_unaffected(sample_chunk) -> None:
    # The full/combined builder has no dedicated maintenance_task guidance
    # paragraph at all (confirmed by reading full_extraction_prompt_builder.py)
    # and does not import MAINTENANCE_TASK_GUIDANCE - it must not pick up
    # this change. Per instruction: do not touch the full MULTI_FAMILY
    # prompt here.
    prompt = CombinedExtractionPromptBuilder().build(
        sample_chunk.document_id, [sample_chunk]
    )

    assert MAINTENANCE_TASK_GUIDANCE not in prompt
    assert '"maintenance_tasks": [' in prompt
