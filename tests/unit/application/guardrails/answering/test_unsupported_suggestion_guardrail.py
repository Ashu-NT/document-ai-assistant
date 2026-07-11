from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.violation_type import ViolationType
from src.application.guardrails.answering.unsupported_suggestion_guardrail import (
    UnsupportedSuggestionGuardrail,
)
from src.application.guardrails.policies.answer_guardrail_policy import (
    AnswerGuardrailPolicy,
)


def _supported_section(heading: str = "Heading") -> dict:
    return {"heading": heading, "body": "Body text.", "reference_note_ids": ["r1"]}


def _unsupported_section(heading: str = "Heading") -> dict:
    return {"heading": heading, "body": "Body text.", "reference_note_ids": []}


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = UnsupportedSuggestionGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_disabled_by_policy() -> None:
    guardrail = UnsupportedSuggestionGuardrail(
        AnswerGuardrailPolicy(block_unsupported_suggestions=False)
    )
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="procedure_steps",
        sections=[_unsupported_section()],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_when_intent_is_not_prescriptive() -> None:
    guardrail = UnsupportedSuggestionGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="general",
        sections=[_unsupported_section()],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_when_all_sections_supported() -> None:
    guardrail = UnsupportedSuggestionGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="procedure_steps",
        sections=[_supported_section("A"), _supported_section("B")],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_flags_unsupported_prescriptive_section_without_blocking() -> None:
    guardrail = UnsupportedSuggestionGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        answer_intent="troubleshooting",
        sections=[_supported_section("Supported"), _unsupported_section("Unsupported")],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.ALLOW_WITH_CAUTION
    assert len(result.violations) == 1
    violation = result.violations[0]
    assert violation.violation_type == ViolationType.GROUNDING_FAILURE
    assert violation.field == "sections"
    assert "Unsupported" in violation.description
