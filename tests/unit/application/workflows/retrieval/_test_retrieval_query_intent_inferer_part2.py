"""Unit tests for RetrievalQueryIntentInferer."""

import pytest

from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent

from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)

from src.domain.common import ChunkType

from src.domain.retrieval import RetrievalQuery

def _make_query(text: str, chunk_types: list[ChunkType] | None = None) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="q_test",
        query_text=text,
        chunk_types=chunk_types or [],
    )

inferer = RetrievalQueryIntentInferer()

class TestNegationAwareness:
    def test_negated_marker_does_not_trigger_its_intent(self) -> None:
        query = _make_query("Not a safety concern here.")
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert RetrievalQueryIntent.SAFETY not in classification.scores

    def test_unnegated_marker_still_triggers_its_intent(self) -> None:
        query = _make_query("This is a safety concern.")
        assert inferer.infer(query) == RetrievalQueryIntent.SAFETY

    def test_multi_word_negation_cue_suppresses_marker(self) -> None:
        query = _make_query("Please describe topics unrelated to safety compliance.")
        classification = inferer.classify(query)
        assert RetrievalQueryIntent.SAFETY not in classification.scores

    def test_negation_cue_outside_lookback_window_does_not_suppress_marker(
        self,
    ) -> None:
        """'not' is more than 4 tokens before 'safety' here, so it's outside
        the negation lookback window and should not suppress the marker."""
        query = _make_query(
            "The pump was not running well, but there is a safety issue too."
        )
        classification = inferer.classify(query)
        assert RetrievalQueryIntent.SAFETY in classification.scores

    def test_negation_falls_back_to_a_second_valid_occurrence(self) -> None:
        """'danger' appears twice: the first occurrence is negated, the
        second is not -- the marker should still register since at least
        one non-negated occurrence exists."""
        query = _make_query(
            "This message is not about danger, but the yellow tag indicates "
            "danger to operators."
        )
        classification = inferer.classify(query)
        assert RetrievalQueryIntent.SAFETY in classification.scores

class TestComparativeSignal:
    def test_difference_between_phrase_is_flagged_comparative(self) -> None:
        query = _make_query("What is the difference between valve A and valve B?")
        assert inferer.classify(query).is_comparative is True

    def test_compare_keyword_is_flagged_comparative(self) -> None:
        query = _make_query("Compare the pressure ratings of pump A and pump B.")
        assert inferer.classify(query).is_comparative is True

    def test_vs_marker_is_flagged_comparative(self) -> None:
        query = _make_query("Pump A vs Pump B specifications")
        assert inferer.classify(query).is_comparative is True

    def test_non_comparative_query_is_not_flagged(self) -> None:
        query = _make_query("What is the operating pressure?")
        assert inferer.classify(query).is_comparative is False

    def test_pure_comparative_query_with_no_topic_marker_resolves_to_overview_not_general(
        self,
    ) -> None:
        """'difference between valve A and valve B' has no FIGURE/TABLE/
        IDENTIFIER/SPECIFICATION/etc. marker at all -- before the comparative
        fallback tier existed this fell all the way to GENERAL (no chunk-type
        preference whatsoever). OVERVIEW's broad preference list is a
        materially better default for a comparison question with an unknown
        topic."""
        query = _make_query("What is the difference between valve A and valve B?")
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.OVERVIEW
        assert classification.resolution_tier == "comparative_fallback"
        assert classification.is_comparative is True
        assert classification.confidence == 0.3

    def test_comparative_fallback_does_not_preempt_a_real_topic_marker(self) -> None:
        """A comparative query that DOES have a topic marker must still be
        resolved by the normal scored path -- the fallback only applies when
        scoring finds nothing at all."""
        query = _make_query(
            "What is the difference between the operating pressure of pump A "
            "and pump B?"
        )
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.SPECIFICATION
        assert classification.resolution_tier == "scored"

    def test_comparative_fallback_does_not_preempt_the_identifier_fallback(
        self,
    ) -> None:
        """A comparative query with a detected identifier and no topic
        marker should still prefer the identifier_fallback tier over the
        comparative one -- a concrete identifier is a stronger signal than a
        comparison shape."""
        query = RetrievalQuery(
            query_id="q_comparative_identifier",
            query_text="What is the difference between FWC12 and FWC13?",
            detected_identifiers=["fwc12", "fwc13"],
        )
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.IDENTIFIER
        assert classification.resolution_tier == "identifier_fallback"

    def test_comparative_flag_does_not_change_the_winning_intent(self) -> None:
        """The comparative flag is additive signal, not a routing decision --
        a comparative SPECIFICATION query should still resolve to
        SPECIFICATION, just with is_comparative=True alongside it."""
        query = _make_query(
            "What is the difference between the operating pressure of pump A "
            "and pump B?"
        )
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.SPECIFICATION
        assert classification.is_comparative is True
