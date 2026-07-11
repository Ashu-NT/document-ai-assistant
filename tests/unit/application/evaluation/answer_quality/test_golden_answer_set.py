from src.application.evaluation.answer_quality import (
    GoldenAnswerCase,
    load_golden_answer_cases,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


def test_load_golden_answer_cases_returns_between_15_and_20_cases() -> None:
    cases = load_golden_answer_cases()

    assert 15 <= len(cases) <= 20
    assert all(isinstance(case, GoldenAnswerCase) for case in cases)


def test_load_golden_answer_cases_returns_a_fresh_list_each_call() -> None:
    first = load_golden_answer_cases()
    second = load_golden_answer_cases()

    assert first is not second
    first.clear()
    assert len(second) > 0


def test_case_ids_are_unique() -> None:
    cases = load_golden_answer_cases()

    case_ids = [case.case_id for case in cases]
    assert len(case_ids) == len(set(case_ids))


def test_every_case_has_required_fields_populated() -> None:
    cases = load_golden_answer_cases()

    for case in cases:
        assert case.case_id
        assert case.document_title
        assert case.question
        assert case.expected_answer
        assert len(case.expected_claims) >= 2
        assert len(case.expected_claims) <= 4
        assert case.expected_citation_hint


def test_cases_span_multiple_answer_intents() -> None:
    cases = load_golden_answer_cases()

    intents = {case.expected_intent for case in cases if case.expected_intent}
    assert len(intents) >= 4


def test_cases_span_multiple_documents() -> None:
    cases = load_golden_answer_cases()

    document_titles = {case.document_title for case in cases}
    assert len(document_titles) >= 5


def test_general_answer_intent_is_represented() -> None:
    cases = load_golden_answer_cases()

    assert any(case.expected_intent == AnswerIntent.GENERAL for case in cases)
