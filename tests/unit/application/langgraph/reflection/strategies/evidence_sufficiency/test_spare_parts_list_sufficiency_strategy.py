from tests.unit.application.langgraph.reflection.strategies.evidence_sufficiency._evidence_sufficiency_test_helpers import (
    make_context,
)

from src.application.langgraph.reflection.models import SufficiencyVerdictType
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    SparePartsListEvidenceSufficiencyStrategy,
)

_SPARE_PARTS_CHUNK = {
    "document_id": "doc_1",
    "chunk_type": "spare_parts_table",
    "content": "Spare parts list: Filter A00103.",
}

_GROUNDED_SPARE_PARTS_ANSWER = (
    "Spare parts lists found:\n\n"
    "1. Spare Parts List\n"
    "   Pages: 85-87\n"
    "   Description: Filter\n"
    "   Part No.: A00103\n"
)


def test_spare_parts_strategy_is_sufficient_for_a_grounded_partial_answer() -> None:
    strategy = SparePartsListEvidenceSufficiencyStrategy()
    context = make_context(
        question="What is the spare parts list for the pump?",
        answer_text=_GROUNDED_SPARE_PARTS_ANSWER,
        approved_chunks=[_SPARE_PARTS_CHUNK],
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT


def test_spare_parts_strategy_is_insufficient_when_answer_denies_the_list_exists() -> None:
    strategy = SparePartsListEvidenceSufficiencyStrategy()
    context = make_context(
        question="What is the spare parts list for the pump?",
        answer_text="No spare parts list was found in the document.",
        approved_chunks=[_SPARE_PARTS_CHUNK],
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.INSUFFICIENT_RETRY
    assert "spare parts table rows" in verdict.missing_information


def test_spare_parts_strategy_falls_back_to_generic_for_non_spare_parts_question() -> None:
    strategy = SparePartsListEvidenceSufficiencyStrategy()
    context = make_context(
        question="What is the operating pressure?",
        answer_text="The operating pressure is 6 bar.",
        approved_chunks=[_SPARE_PARTS_CHUNK],
    )

    verdict = strategy.is_answer_sufficient(context)

    assert verdict.verdict == SufficiencyVerdictType.SUFFICIENT
