from src.application.services.answer_generation.formatting.policy.answer_format_policy import (
    AnswerFormatPolicy,
)
from src.application.services.answer_generation.formatting.policy.format_policy_violation_detector import (
    detect_format_policy_violations,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


def _policy(
    *,
    include_steps: bool = False,
    include_bullets: bool = False,
    include_table: bool = False,
) -> AnswerFormatPolicy:
    return AnswerFormatPolicy(
        intent=AnswerIntent.GENERAL,
        preferred_format="prose",
        include_table=include_table,
        include_bullets=include_bullets,
        include_steps=include_steps,
        max_bullets=None,
        response_label="Answer",
        instruction_lines=(),
    )


def test_detect_returns_no_violations_when_policy_is_none() -> None:
    assert detect_format_policy_violations(format_policy=None, answer_text="anything") == []


def test_detect_returns_no_violations_for_empty_answer_text() -> None:
    policy = _policy(include_steps=True)
    assert detect_format_policy_violations(format_policy=policy, answer_text="") == []


def test_detect_returns_no_violations_when_no_structural_requirements_are_set() -> None:
    policy = _policy()
    text = "This is a plain prose answer with no lists or tables."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == []


def test_detect_flags_missing_numbered_steps() -> None:
    policy = _policy(include_steps=True)
    text = "First, replace the filter. Then close the housing."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == [
        "missing_numbered_steps"
    ]


def test_detect_passes_when_numbered_steps_are_present() -> None:
    policy = _policy(include_steps=True)
    text = "1. Remove the cover.\n2. Replace the filter.\n3. Reinstall the cover."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == []


def test_detect_flags_missing_bullets() -> None:
    policy = _policy(include_bullets=True)
    text = "Some prose without any bullet markers at all."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == [
        "missing_bullets"
    ]


def test_detect_passes_when_bullets_are_present() -> None:
    policy = _policy(include_bullets=True)
    text = "- Item one\n- Item two"
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == []


def test_detect_flags_missing_table() -> None:
    policy = _policy(include_table=True)
    text = "The spec is 700 bar, no table here."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == [
        "missing_table"
    ]


def test_detect_passes_when_table_rows_are_present() -> None:
    policy = _policy(include_table=True)
    text = "| Parameter | Value |\n| Test pressure | 700 bar |"
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == []


def test_detect_reports_multiple_violations_together() -> None:
    policy = _policy(include_steps=True, include_bullets=True, include_table=True)
    text = "Plain prose with no structure whatsoever."
    assert detect_format_policy_violations(format_policy=policy, answer_text=text) == [
        "missing_numbered_steps",
        "missing_bullets",
        "missing_table",
    ]
