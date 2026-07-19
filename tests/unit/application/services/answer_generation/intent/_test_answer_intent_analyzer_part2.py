import logging

from src.application.services.answer_generation.intent import (
    AnswerIntent,
    AnswerIntentAnalyzer,
)

from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    ANSWER_INTENT_RULES_VERSION,
)

from src.domain.common import ChunkType

from src.domain.common.source_location import SourceLocation

from src.domain.retrieval.retrieved_chunk import RetrievedChunk

def _make_chunk(
    *,
    content: str,
    chunk_type: ChunkType = ChunkType.GENERAL,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=["Section"],
        source=SourceLocation(page_start=1, page_end=1),
        metadata=metadata or {},
    )

def test_unambiguous_question_has_no_runner_up() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="This is a safety warning.")

    assert decision.runner_up_intent is None
    assert decision.runner_up_score == 0
    assert decision.margin is None
    assert decision.is_contested is False

def test_empty_question_falls_back_to_general_with_no_runner_up() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="")

    assert decision.intent == AnswerIntent.GENERAL
    assert decision.confidence == 0.55
    assert decision.runner_up_intent is None
    assert decision.runner_up_score == 0

def test_question_with_no_recognizable_terms_falls_back_to_general() -> None:
    decision = AnswerIntentAnalyzer().analyze(question="asdkjaslkdj")

    assert decision.intent == AnswerIntent.GENERAL
    assert decision.confidence == 0.55

def test_resolved_intent_is_logged_with_rules_version(caplog) -> None:
    with caplog.at_level(logging.INFO):
        AnswerIntentAnalyzer().analyze(question="This is a safety warning.")

    assert "answer_intent_resolved" in caplog.text
    assert "intent=safety_warnings" in caplog.text
    assert f"rules_version={ANSWER_INTENT_RULES_VERSION}" in caplog.text

def test_general_fallback_is_logged_with_reason(caplog) -> None:
    with caplog.at_level(logging.INFO):
        AnswerIntentAnalyzer().analyze(question="")

    assert "answer_intent_fallback_general" in caplog.text
    assert "reason=no_strong_signal" in caplog.text

def test_resolved_intent_log_line_carries_margin_and_runner_up_telemetry(caplog) -> None:
    """Prerequisite for ever widening AnswerIntentDecision.is_contested past
    an exact tie: the margin must actually be observable, not just computed
    and discarded (the same "make observability real" gap this session's
    audit flagged elsewhere in this pipeline)."""
    with caplog.at_level(logging.INFO):
        AnswerIntentAnalyzer().analyze(
            question="What is the specification and what is the procedure to install it?"
        )

    assert "margin=0" in caplog.text
    assert "runner_up_intent=procedure_steps" in caplog.text
