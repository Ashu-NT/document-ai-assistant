from src.application.langgraph.reflection.evaluators.answer_quality_scorer import (
    AnswerQualityScorer,
)

_QUESTION = "What is the pump maximum flow rate specification?"
# A fluent-but-wrong answer: answers the question, cites a source, repeats
# question terms, is short -- would score a perfect 6/6 under the old scorer.
_FLUENT_BUT_WRONG_ANSWER = (
    "The pump maximum flow rate specification is 120 m3/h, as shown on page 4."
)
_CITATIONS = [{"chunk_id": "chunk_4", "source": {"page_start": 4}}]


def test_reference_notes_omitted_is_byte_identical_to_before_the_change() -> None:
    """Mandatory backward-compatibility test."""
    without_param = AnswerQualityScorer.score(
        question=_QUESTION,
        answer=_FLUENT_BUT_WRONG_ANSWER,
        citations=_CITATIONS,
    )
    with_explicit_none = AnswerQualityScorer.score(
        question=_QUESTION,
        answer=_FLUENT_BUT_WRONG_ANSWER,
        citations=_CITATIONS,
        reference_notes=None,
    )

    assert without_param == with_explicit_none
    assert without_param.score == 1.0


def test_unresolved_reference_note_caps_an_otherwise_perfect_score() -> None:
    """Reproduces finding 4.3: a fluent-but-wrong answer with a hallucinated
    (unresolved) citation must never score a perfect 6/6 -- it must be capped
    at a clearly-lower ceiling, regardless of how many other signals pass."""
    result = AnswerQualityScorer.score(
        question=_QUESTION,
        answer=_FLUENT_BUT_WRONG_ANSWER,
        citations=_CITATIONS,
        reference_notes=[
            {
                "note_id": "r1",
                "claim_text": "The pump maximum flow rate is 120 m3/h.",
                "source_number": 1,
                "chunk_id": None,
            }
        ],
    )

    assert result.score <= 0.5
    assert "unresolved_reference_citation" in result.issues


def test_fully_resolved_reference_notes_do_not_cap_the_score() -> None:
    result = AnswerQualityScorer.score(
        question=_QUESTION,
        answer=_FLUENT_BUT_WRONG_ANSWER,
        citations=_CITATIONS,
        reference_notes=[
            {
                "note_id": "r1",
                "claim_text": "The pump maximum flow rate is 120 m3/h.",
                "source_number": 1,
                "chunk_id": "chunk_4",
            }
        ],
    )

    assert result.score == 1.0
    assert "unresolved_reference_citation" not in result.issues


def test_empty_reference_notes_list_does_not_cap_the_score() -> None:
    result = AnswerQualityScorer.score(
        question=_QUESTION,
        answer=_FLUENT_BUT_WRONG_ANSWER,
        citations=_CITATIONS,
        reference_notes=[],
    )

    assert result.score == 1.0


def test_answer_quality_flags_unexpected_answer_pages_against_approved_scope() -> None:
    result = AnswerQualityScorer.score(
        question=_QUESTION,
        answer="The pump maximum flow rate is 120 m3/h, as shown on page 99.",
        citations=[{"chunk_id": "chunk_99", "source": {"page_start": 99}}],
        approved_pages=[4],
    )

    assert "unexpected_answer_pages" in result.issues
    assert result.unexpected_pages == [99]
    assert result.score < 1.0


def test_answer_quality_detects_duplicate_content_lines() -> None:
    result = AnswerQualityScorer.score(
        question="What are the maintenance intervals?",
        answer=(
            "- Weekly maintenance latest after 100 operating hours.\n"
            "- Weekly maintenance latest after 100 operating hours.\n"
            "- Annual maintenance latest after 2000 operating hours."
        ),
        citations=[{"chunk_id": "chunk_58", "source": {"page_start": 58}}],
        approved_pages=[58],
    )

    assert "duplicate_answer_content" in result.issues
    assert result.has_duplicate_content is True
    assert result.duplicate_line_count == 1
