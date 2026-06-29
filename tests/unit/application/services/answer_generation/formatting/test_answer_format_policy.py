from src.application.services.answer_generation import AnswerFormatPolicy, AnswerIntent


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

    assert policy.preferred_format == "ordered_bullets"
    assert any("Preserve stated intervals exactly." == line for line in policy.instruction_lines)


def test_procedure_policy_uses_numbered_steps() -> None:
    policy = AnswerFormatPolicy.for_intent(AnswerIntent.PROCEDURE_STEPS)

    assert policy.include_steps is True
    assert policy.include_bullets is False
    assert policy.preferred_format == "numbered_steps"
