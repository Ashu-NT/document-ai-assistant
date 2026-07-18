from tests.unit.application.langgraph.reflection.strategies.evidence_sufficiency._evidence_sufficiency_test_helpers import (
    make_context,
)

from src.application.langgraph.reflection.models import SufficiencyVerdictType
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    IdentifierInventoryEvidenceSufficiencyStrategy,
)


def test_identifier_strategy_is_sufficient_when_answer_lists_identifier_values() -> None:
    strategy = IdentifierInventoryEvidenceSufficiencyStrategy()
    context = make_context(
        question="List all part numbers and serial numbers.",
        answer_intent="identifier_lookup",
        answer_text="Part numbers: PN-001, PN-002. Serial numbers: SN-9001.",
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_identifier_strategy_is_insufficient_when_answer_omits_identifier_values() -> None:
    strategy = IdentifierInventoryEvidenceSufficiencyStrategy()
    context = make_context(
        question="List all part numbers and serial numbers.",
        answer_intent="identifier_lookup",
        answer_text="Several identifiers are documented in the manual.",
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
    assert "explicit identifier values" in verdict.missing_information


def test_identifier_strategy_falls_back_to_generic_for_a_non_listing_question() -> None:
    strategy = IdentifierInventoryEvidenceSufficiencyStrategy()
    context = make_context(
        question="What is the operating pressure?",
        answer_intent="specification_summary",
        answer_text="The operating pressure is 6 bar.",
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT
