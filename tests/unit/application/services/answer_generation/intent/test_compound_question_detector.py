from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.intent.compound_question_detector import (
    CompoundQuestionDetector,
)


def test_detects_an_unrelated_intent_signal_after_a_conjunction() -> None:
    detector = CompoundQuestionDetector()

    detected = detector.detect(
        question="What are the spare parts and how do I replace the seal?",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert detected == AnswerIntent.PROCEDURE_STEPS


def test_returns_none_for_a_non_compound_question() -> None:
    detector = CompoundQuestionDetector()

    detected = detector.detect(
        question="What are the spare part numbers?",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert detected is None


def test_does_not_flag_identifier_and_table_summary_as_mutually_unrelated() -> None:
    """IDENTIFIER_LOOKUP and TABLE_SUMMARY overlap heavily in real questions
    (a parts list is both) -- flagging the pair as "compound" against each
    other would false-positive on almost every parts-table question."""
    detector = CompoundQuestionDetector()

    detected = detector.detect(
        question="Show me the parts table and list all part numbers",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert detected is None


def test_returns_none_for_empty_or_none_question() -> None:
    detector = CompoundQuestionDetector()

    assert detector.detect(question="", driving_intent=None) is None
    assert detector.detect(question=None, driving_intent=None) is None
