from src.application.contracts.guardrails import GuardrailDecision
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.guardrails.answering.conflicting_evidence_guardrail import (
    ConflictingEvidenceGuardrail,
)


def _conflict(document_ids: list[str], is_critical: bool = True) -> dict:
    return {
        "key": "operating pressure",
        "field_kind": "specification",
        "values": ["6 bar", "8 bar"],
        "source_numbers": [1, 2],
        "is_critical": is_critical,
        "document_ids": document_ids,
    }


def test_check_allows_when_no_answer_to_validate() -> None:
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(answer_text=None)

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_there_are_no_conflicts() -> None:
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(answer_text="Answer.", metadata={"evidence_conflicts": []})

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_allows_when_conflicts_are_present_but_not_critical() -> None:
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(
        answer_text="Answer.",
        metadata={"evidence_conflicts": [_conflict(["doc_a"], is_critical=False)]},
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
    assert result.allowed is True


def test_check_abstains_for_a_same_document_conflict() -> None:
    """Sign-off decision: abstain by default, no regenerate, name the
    conflict so the user can check the source directly."""
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(
        answer_text="The operating pressure is 6 bar.",
        metadata={"evidence_conflicts": [_conflict(["doc_a"])]},
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.CONFLICTING_EVIDENCE
    assert result.allowed is True
    assert len(result.violations) == 1
    assert "operating pressure" in result.safe_user_message
    assert "6 bar" in result.safe_user_message and "8 bar" in result.safe_user_message


def test_check_requests_clarification_for_a_cross_document_conflict() -> None:
    """Sign-off decision: route to CLARIFY only when the disagreement is
    demonstrably caused by an undisambiguated equipment/revision scope --
    proxied here by the conflicting sources spanning more than one
    document_id."""
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(
        answer_text="The operating pressure is 6 bar.",
        metadata={"evidence_conflicts": [_conflict(["doc_a", "doc_b"])]},
    )

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.NEEDS_CLARIFICATION
    assert result.allowed is True
    assert "which one" in result.safe_user_message.lower()


def test_check_treats_missing_metadata_as_no_conflict() -> None:
    guardrail = ConflictingEvidenceGuardrail()
    context = GuardrailContext(answer_text="Answer.")

    result = guardrail.check(context)

    assert result.decision == GuardrailDecision.ALLOW
