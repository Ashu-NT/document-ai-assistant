from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.answering.unsupported_claim_guardrail import (
    UnsupportedClaimGuardrail,
)
from src.application.guardrails.policies.answer_guardrail_policy import (
    AnswerGuardrailPolicy,
)


def _supported_section(heading: str = "Heading") -> dict:
    return {"heading": heading, "body": "Body text.", "reference_note_ids": ["r1"]}


def _unsupported_section(heading: str = "Heading") -> dict:
    return {"heading": heading, "body": "Body text.", "reference_note_ids": []}


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = UnsupportedClaimGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_block_unsupported_claims_disabled_by_policy() -> None:
    guardrail = UnsupportedClaimGuardrail(
        AnswerGuardrailPolicy(block_unsupported_claims=False)
    )
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[_unsupported_section()],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_when_every_section_has_reference_notes() -> None:
    guardrail = UnsupportedClaimGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[_supported_section("A"), _supported_section("B")],
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True
    assert result.violations == []


def test_check_allows_with_no_sections_at_all() -> None:
    guardrail = UnsupportedClaimGuardrail()
    context = GuardrailContext(answer_text="Answer.", sections=[])

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_flags_unsupported_sections_without_blocking() -> None:
    guardrail = UnsupportedClaimGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        sections=[_supported_section("Supported"), _unsupported_section("Unsupported")],
    )

    result = guardrail.check(context)

    assert result.allowed is True
    assert result.decision == GuardrailDecision.UNSUPPORTED_CLAIMS
    assert len(result.violations) == 1
    violation = result.violations[0]
    assert violation.field == "sections"
    assert "Unsupported" in violation.description
