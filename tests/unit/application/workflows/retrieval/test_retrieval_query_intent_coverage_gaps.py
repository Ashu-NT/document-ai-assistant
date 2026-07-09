"""Regression tests for query-understanding coverage gaps identified during
the Phase 4 enterprise-hardening review: one-word queries, typos in the
trigger markers themselves, multi-intent/near-tie queries beyond the existing
characterization tests, non-English text, and the rewriter-then-intent
interaction. Several of these document a KNOWN, ACCEPTED gap (no typo
tolerance, no non-English support) rather than a bug -- the deterministic
layer is intentionally literal; low-confidence/GENERAL results on these
inputs are exactly the signal the future LLM-clarification layer (Phase 5)
is meant to catch."""

from src.application.workflows.retrieval.retrieval_query_analyzer import (
    RetrievalQueryAnalyzer,
)
from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.retrieval import RetrievalQuery


def _make_query(text: str) -> RetrievalQuery:
    return RetrievalQuery(query_id="q_test", query_text=text)


inferer = RetrievalQueryIntentInferer()
analyzer = RetrievalQueryAnalyzer()


# ---------------------------------------------------------------------------
# One-word queries
# ---------------------------------------------------------------------------

class TestOneWordQueries:
    def test_single_keyword_marker_resolves_at_the_minimum_score(self) -> None:
        classification = inferer.classify(_make_query("safety"))
        assert classification.intent == RetrievalQueryIntent.SAFETY
        assert classification.score == 4
        assert classification.runner_up_intent is None

    def test_single_word_with_no_marker_falls_back_to_general(self) -> None:
        classification = inferer.classify(_make_query("pump"))
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert classification.fallback_reason == "no_pattern_matched"


# ---------------------------------------------------------------------------
# Typos in the trigger markers themselves -- the deterministic layer does
# plain substring matching with no fuzzy/typo tolerance. A typo inside the
# ONLY marker word present causes a complete miss, not a degraded match.
# This is a known, accepted gap: it's exactly the low-confidence signal the
# future LLM clarification layer should act on, not something the
# deterministic layer should silently paper over with fuzzy matching.
# ---------------------------------------------------------------------------

class TestTyposInTriggerMarkersAreNotTolerated:
    def test_typo_in_the_only_troubleshooting_marker_misses_entirely(self) -> None:
        classification = inferer.classify(
            _make_query("How do I troublshoot the pump?")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert RetrievalQueryIntent.TROUBLESHOOTING not in classification.scores

    def test_typo_in_the_only_specification_marker_misses_entirely(self) -> None:
        classification = inferer.classify(_make_query("What is the presure range?"))
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert RetrievalQueryIntent.SPECIFICATION not in classification.scores

    def test_typo_in_troubleshooting_marker_still_recovers_via_a_second_intact_marker(
        self,
    ) -> None:
        """'cuases' is a typo, but 'vibration' isn't a marker either -- this
        query only has ONE candidate marker and it's misspelled, so unlike
        the existing test_identifier_inventory_query_with_typo_still_maps_to_
        identifier case (where the typo is in an incidental word, not the
        marker itself), there's no fallback signal left and it lands on
        GENERAL. Documented here as the contrasting case."""
        classification = inferer.classify(
            _make_query("What are the likely cuases of pump vibration?")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL


# ---------------------------------------------------------------------------
# Multi-intent / near-tie queries beyond the existing TABLE/IDENTIFIER
# characterization test.
# ---------------------------------------------------------------------------

class TestMultiIntentAndNearTieQueries:
    def test_exact_score_tie_resolves_via_priority_rank_not_the_required_gap_override(
        self,
    ) -> None:
        """MAINTENANCE and PROCEDURE both score exactly 4 (one marker hit
        each) here -- an EXACT tie, gap=0. This is a distinct code path from
        test_maintenance_signal_overwhelms_incidental_procedure_marker (which
        has a real gap that must clear the required_gap=4 override): an
        exact tie short-circuits straight to the priority-rank tie-break
        (MAINTENANCE ranked before PROCEDURE) without ever consulting
        _REQUIRED_GAP_OVERRIDES."""
        classification = inferer.classify(
            _make_query("What is the maintenance procedure for replacing the filter?")
        )
        assert classification.intent == RetrievalQueryIntent.MAINTENANCE
        assert classification.runner_up_intent == RetrievalQueryIntent.PROCEDURE
        assert classification.score == classification.runner_up_score == 4

    def test_two_strong_markers_for_one_intent_clearly_beat_a_single_marker_runner_up(
        self,
    ) -> None:
        classification = inferer.classify(
            _make_query("Show me the safety warning table.")
        )
        assert classification.intent == RetrievalQueryIntent.SAFETY
        assert classification.score == 8
        assert classification.runner_up_intent == RetrievalQueryIntent.TABLE
        assert classification.runner_up_score == 4

    def test_specification_and_troubleshooting_both_present_specification_wins_clearly(
        self,
    ) -> None:
        classification = inferer.classify(
            _make_query(
                "What is the pressure specification and troubleshooting procedure?"
            )
        )
        assert classification.intent == RetrievalQueryIntent.SPECIFICATION
        assert classification.runner_up_intent == RetrievalQueryIntent.TROUBLESHOOTING
        assert classification.gap == 4


# ---------------------------------------------------------------------------
# Non-English text -- this corpus includes German documents, but every
# marker/pattern in the deterministic layer is English-only. A German query
# with no English loanwords always falls through to GENERAL. Documented as a
# known, accepted gap: translating or detecting language deterministically
# is out of scope for this layer -- it's a candidate trigger condition for
# the future LLM clarification layer.
# ---------------------------------------------------------------------------

class TestNonEnglishTextFallsBackToGeneral:
    def test_german_maintenance_interval_question_is_not_recognized(self) -> None:
        classification = inferer.classify(
            _make_query("Wie oft muss die Wartung durchgefuehrt werden?")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert classification.scores == {}

    def test_german_specification_question_is_not_recognized(self) -> None:
        classification = inferer.classify(
            _make_query("Was ist der Nenndruck der Pumpe?")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL

    def test_german_safety_question_is_not_recognized(self) -> None:
        classification = inferer.classify(
            _make_query("Sicherheitshinweis fuer die Wartung")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL


# ---------------------------------------------------------------------------
# Rewriter -> intent interaction: RetrievalQueryAnalyzer.analyze() rewrites
# the query BEFORE inferring intent, and the inferer reads
# query.effective_query() (rewritten_query if set, else query_text). This
# proves the RetrievalQueryRewriter case-sensitivity fix has a real,
# behavior-changing effect on classification -- not just cosmetic
# normalization -- for abbreviations with no separate literal-marker
# fallback of their own.
# ---------------------------------------------------------------------------

class TestRewriterIntentInteraction:
    def test_capitalized_drawing_abbreviation_only_resolves_to_identifier_after_rewrite(
        self,
    ) -> None:
        """'Dwg No.' has no marker of its own (the FIGURE/IDENTIFIER marker
        lists only recognize the expanded word 'drawing', not the
        abbreviation) -- it depends entirely on the rewriter's case-insensitive
        abbreviation expansion to become classifiable. Analyzed end-to-end via
        RetrievalQueryAnalyzer (not classify() directly) so the rewrite step
        actually runs before intent inference, matching the production path."""
        analyzed = analyzer.analyze(
            RetrievalQuery(query_id="q_dwg", query_text="What is Dwg No. AB123-45?")
        )
        assert analyzed.rewritten_query == "What is drawing number AB123-45?"

        classification = inferer.classify(analyzed)
        assert classification.intent == RetrievalQueryIntent.IDENTIFIER
        assert RetrievalQueryIntent.FIGURE in classification.scores

    def test_without_the_rewrite_the_same_abbreviation_would_fall_back_to_general(
        self,
    ) -> None:
        """Characterizes the pre-fix failure mode directly: classifying the
        raw, un-rewritten capitalized text (as the case-sensitive bug would
        have left it) finds no marker at all."""
        classification = inferer.classify(
            RetrievalQuery(query_id="q_dwg_raw", query_text="What is Dwg No. AB123-45?")
        )
        assert classification.intent == RetrievalQueryIntent.GENERAL

    def test_lowercase_abbreviation_variant_also_expands_and_resolves_to_identifier(
        self,
    ) -> None:
        analyzed = analyzer.analyze(
            RetrievalQuery(query_id="q_dwg_lower", query_text="what is dwg no. ab123-45?")
        )
        assert analyzed.rewritten_query == "what is drawing number ab123-45?"
        classification = inferer.classify(analyzed)
        assert classification.intent == RetrievalQueryIntent.IDENTIFIER
