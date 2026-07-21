from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.intent.compound_question_detector import (
    CompoundQuestionDetector,
    chunks_plausibly_cover_intent,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _chunk(content: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_1",
        document_id="doc_1",
        content=content,
        score=0.9,
        retrieval_source="dense",
    )


def test_detects_an_unrelated_intent_signal_after_a_conjunction() -> None:
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="What are the spare parts and how do I replace the seal?",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert signal.is_compound is True
    assert signal.reason == "conjunction"
    assert signal.unrelated_intent == AnswerIntent.PROCEDURE_STEPS
    assert signal.clauses == (
        "What are the spare parts",
        "how do I replace the seal?",
    )


def test_detects_two_clauses_split_on_a_multi_part_question_mark() -> None:
    """PR 6 (answering_flow_weakness_remediation_plan.md): reusing
    QuestionClauseSplitter picks up the multi-question-mark expansion for
    free -- a second, standalone question sentence is just as compound as
    a conjunction, even with no "and" anywhere in the text."""
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="What are the spare parts? How do I replace the seal?",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert signal.is_compound is True
    assert signal.reason == "multi_question_mark"
    assert signal.unrelated_intent == AnswerIntent.PROCEDURE_STEPS


def test_detects_two_clauses_split_on_enumerated_markers() -> None:
    """W3 (answering_flow_weakness_remediation_plan.md): the previously
    deferred enumerated-request expansion tier, now handled by
    QuestionClauseSplitter -- picked up here for free, same as the
    multi-question-mark case above."""
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="Tell me: 1) the spare parts 2) how do I replace the seal",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert signal.is_compound is True
    assert signal.reason == "enumerated_list"
    assert signal.unrelated_intent == AnswerIntent.PROCEDURE_STEPS


def test_returns_not_compound_for_a_non_compound_question() -> None:
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="What are the spare part numbers?",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert signal.is_compound is False
    assert signal.unrelated_intent is None
    assert signal.clauses is None


def test_does_not_flag_identifier_and_table_summary_as_mutually_unrelated() -> None:
    """IDENTIFIER_LOOKUP and TABLE_SUMMARY overlap heavily in real questions
    (a parts list is both) -- flagging the pair as "compound" against each
    other would false-positive on almost every parts-table question."""
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="Show me the parts table and list all part numbers",
        driving_intent=AnswerIntent.IDENTIFIER_LOOKUP,
    )

    assert signal.is_compound is False


def test_does_not_over_trigger_on_a_plain_noun_phrase_conjunction() -> None:
    """PR 6's explicit acceptance criterion: a noun-phrase "and" with no
    question-trigger word after it (mirroring QuestionClauseSplitter's own
    false-positive guard) must stay a single request, not a false compound."""
    detector = CompoundQuestionDetector()

    signal = detector.detect(
        question="What are the inspection and certification requirements?",
        driving_intent=AnswerIntent.SPECIFICATION_SUMMARY,
    )

    assert signal.is_compound is False


def test_returns_not_compound_for_empty_or_none_question() -> None:
    detector = CompoundQuestionDetector()

    assert detector.detect(question="", driving_intent=None).is_compound is False
    assert detector.detect(question=None, driving_intent=None).is_compound is False


def test_chunks_plausibly_cover_intent_finds_a_matching_term() -> None:
    chunks = [_chunk("Replace hydraulic filter every 1000 operating hours.")]

    assert chunks_plausibly_cover_intent(chunks, AnswerIntent.PROCEDURE_STEPS) is True


def test_chunks_plausibly_cover_intent_returns_false_with_no_matching_term() -> None:
    chunks = [_chunk("Spare part A00103 (Filter), quantity 2.")]

    assert chunks_plausibly_cover_intent(chunks, AnswerIntent.PROCEDURE_STEPS) is False


def test_chunks_plausibly_cover_intent_returns_false_for_no_intent() -> None:
    chunks = [_chunk("Replace hydraulic filter every 1000 operating hours.")]

    assert chunks_plausibly_cover_intent(chunks, None) is False
