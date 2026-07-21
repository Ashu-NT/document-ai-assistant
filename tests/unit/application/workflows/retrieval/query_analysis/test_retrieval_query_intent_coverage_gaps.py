"""Regression tests for query-understanding coverage gaps identified during
the Phase 4 enterprise-hardening review: one-word queries, typo tolerance via
the fuzzy fallback tier, multi-intent/near-tie queries beyond the existing
characterization tests, non-English text, and the rewriter-then-intent
interaction. Non-English text still documents a KNOWN, ACCEPTED gap (no
translation/language detection) rather than a bug -- low-confidence/GENERAL
results on that input are exactly the signal the future LLM-clarification
layer (Phase 5) is meant to catch."""

from src.application.workflows.retrieval.query_analysis.retrieval_query_analyzer import (
    RetrievalQueryAnalyzer,
)
from src.application.workflows.retrieval.retrieval_query_intent import RetrievalQueryIntent
from src.application.workflows.retrieval.query_analysis.retrieval_query_intent_inferer import (
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
# Typos in the trigger markers themselves. The exact/keyword scoring pass has
# no fuzzy tolerance -- but when it finds nothing at all, a typo-tolerant
# fuzzy fallback (single-word markers only, difflib ratio >= 0.82, tuned
# against real typo examples) gets a second look before giving up to GENERAL.
# ---------------------------------------------------------------------------

class TestTypoTolerantFuzzyFallback:
    def test_typo_in_the_only_troubleshooting_marker_still_resolves_via_fuzzy_match(
        self,
    ) -> None:
        classification = inferer.classify(
            _make_query("How do I troublshoot the pump?")
        )
        assert classification.intent == RetrievalQueryIntent.TROUBLESHOOTING
        assert classification.resolution_tier == "fuzzy_fallback"
        assert classification.confidence == 0.3
        # scores reflects the fuzzy pass's own hits here (the exact pass
        # found nothing, which is exactly why the fuzzy pass ran at all).
        assert classification.scores == {RetrievalQueryIntent.TROUBLESHOOTING: 4}

    def test_typo_in_the_only_specification_marker_still_resolves_via_fuzzy_match(
        self,
    ) -> None:
        classification = inferer.classify(_make_query("What is the presure range?"))
        assert classification.intent == RetrievalQueryIntent.SPECIFICATION
        assert classification.resolution_tier == "fuzzy_fallback"

    def test_typo_recovers_even_when_the_only_other_word_is_also_not_a_marker(
        self,
    ) -> None:
        """'cuases' is a typo of 'causes' and 'vibration' isn't a marker
        either -- this query has exactly one fuzzy-recoverable signal and
        nothing else, yet still resolves instead of falling to GENERAL."""
        classification = inferer.classify(
            _make_query("What are the likely cuases of pump vibration?")
        )
        assert classification.intent == RetrievalQueryIntent.TROUBLESHOOTING
        assert classification.resolution_tier == "fuzzy_fallback"

    def test_fuzzy_pass_still_respects_negation(self) -> None:
        """A near-miss fuzzy match of a token against a marker it's
        VERBATIM (ratio 1.0 -- e.g. a negated 'safety') must not resurrect a
        negated exact hit. A separate, non-negated typo elsewhere in the
        same query still resolves normally."""
        classification = inferer.classify(
            _make_query("Not a safety concern here, but there is a saftey issue too.")
        )
        assert classification.intent == RetrievalQueryIntent.SAFETY
        assert classification.resolution_tier == "fuzzy_fallback"

    def test_exact_marker_match_is_preferred_over_fuzzy_when_both_are_present(
        self,
    ) -> None:
        """Fuzzy fallback only runs when the exact pass finds NOTHING -- a
        query with one correctly-spelled marker must resolve via the normal
        scored path even if another word elsewhere looks like a typo."""
        classification = inferer.classify(
            _make_query("What are the causes of a hazrd on this pump?")
        )
        assert classification.intent == RetrievalQueryIntent.TROUBLESHOOTING
        assert classification.resolution_tier == "scored"

    def test_fuzzy_matching_only_targets_single_word_markers_not_multi_word_phrases(
        self,
    ) -> None:
        """Multi-word markers (e.g. 'service interval') are excluded from the
        fuzzy pool entirely -- fuzzy matching can't reconstruct a two-word
        phrase from one mistyped token. Here 'servide' (typo of 'service')
        has no standalone single-word marker to match, but 'intervl' (typo of
        'interval', which IS also its own standalone MAINTENANCE marker)
        still resolves -- via that single-word marker, not the phrase."""
        classification = inferer.classify(
            _make_query("What is the servide intervl for this pump?")
        )
        assert classification.intent == RetrievalQueryIntent.MAINTENANCE
        assert classification.resolution_tier == "fuzzy_fallback"

    def test_short_words_are_excluded_from_fuzzy_matching_to_avoid_false_positives(
        self,
    ) -> None:
        """Markers/tokens under 5 characters are excluded entirely (e.g.
        'step'/'run') since short-word edit-distance ratios are unreliable
        (compare 'step' vs 'stop') -- a typo of a short marker still misses."""
        classification = inferer.classify(_make_query("What are the setp for this?"))
        assert classification.intent == RetrievalQueryIntent.GENERAL

    def test_a_genuinely_unrelated_word_has_no_fuzzy_near_miss_either(self) -> None:
        classification = inferer.classify(_make_query("pump"))
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert classification.resolution_tier == "general"


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
