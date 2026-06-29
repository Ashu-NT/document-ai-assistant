from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerMaintenanceEntry,
    StructuredAnswerContext,
)


def test_specification_policy_uses_structured_bullets() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.SPECIFICATION_SUMMARY)

    assert policy.preferred_format == "structured_bullets"
    assert policy.include_bullets is True
    assert policy.include_table is True
    assert any(
        "Do not say that specifications are missing" in line
        for line in policy.instruction_lines
    )


def test_maintenance_policy_preserves_intervals() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.MAINTENANCE_SUMMARY)

    assert policy.preferred_format == "structured_maintenance_table"
    assert policy.include_table is True
    assert policy.include_bullets is False
    assert any("Not specified" in line for line in policy.instruction_lines)


def test_maintenance_policy_falls_back_to_checklist_without_structured_entries() -> None:
    context = StructuredAnswerContext(answer_intent=AnswerIntent.MAINTENANCE_SUMMARY)

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=context,
    )

    assert policy.preferred_format == "maintenance_checklist"
    assert policy.include_table is False
    assert policy.include_bullets is True


def test_maintenance_policy_prefers_table_with_structured_entries() -> None:
    context = StructuredAnswerContext(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        maintenance_entries=[
            AnswerMaintenanceEntry(
                task="Replace cartridge filters",
                interval="every 1000 operating hours",
                component="cartridge filters",
                notes=None,
                source_number=1,
            )
        ],
    )

    policy = AnswerFormatPolicy.resolve(
        intent=AnswerIntent.MAINTENANCE_SUMMARY,
        structured_context=context,
    )

    assert policy.preferred_format == "structured_maintenance_table"
    assert policy.include_table is True


def test_procedure_policy_uses_numbered_steps() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.PROCEDURE_STEPS)

    assert policy.include_steps is True
    assert policy.include_bullets is False
    assert policy.preferred_format == "numbered_steps"
