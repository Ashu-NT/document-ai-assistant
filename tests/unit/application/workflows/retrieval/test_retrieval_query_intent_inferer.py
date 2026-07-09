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


# ---------------------------------------------------------------------------
# TROUBLESHOOTING intent: diagnostic-language markers
# ---------------------------------------------------------------------------

class TestTroubleshootingIntent:
    def test_causes_keyword_triggers_troubleshooting(self) -> None:
        query = _make_query("What are the likely causes of pump vibration?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_remedies_keyword_triggers_troubleshooting(self) -> None:
        query = _make_query("What are possible remedies for no flow from the pump?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_causes_and_remedies_together_trigger_troubleshooting(self) -> None:
        query = _make_query(
            "What are likely causes and remedies if the liquor transfer pump runs with no discharge?"
        )
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_diagnose_keyword_triggers_troubleshooting(self) -> None:
        # Avoid "pressure" which would fire SPECIFICATION first
        query = _make_query("How do I diagnose a motor overload condition?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_symptom_keyword_triggers_troubleshooting(self) -> None:
        query = _make_query("What symptom indicates a blocked filter?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_troubleshoot_keyword_still_works(self) -> None:
        query = _make_query("How do I troubleshoot the pump?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_fault_keyword_still_works(self) -> None:
        query = _make_query("The pump has a fault. How can I fix it?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_error_keyword_still_works(self) -> None:
        query = _make_query("Why is there an error on the display?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING


# ---------------------------------------------------------------------------
# TROUBLESHOOTING takes priority over PROCEDURE when both signals present
# ---------------------------------------------------------------------------

class TestTroubleshootingBeforeProcedure:
    def test_causes_beats_run_for_troubleshooting_query(self) -> None:
        """'run' is a PROCEDURE marker, but 'causes' should win as TROUBLESHOOTING
        since it appears earlier in the check order."""
        query = _make_query(
            "What are likely causes if the pump runs continuously?"
        )
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING

    def test_pure_run_query_stays_procedure(self) -> None:
        """A query with 'run' but no troubleshooting markers must remain PROCEDURE."""
        query = _make_query("How do I start and run the macerator?")
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE


# ---------------------------------------------------------------------------
# Other intents not affected
# ---------------------------------------------------------------------------

class TestOtherIntentsUnchanged:
    def test_identifier_inventory_query_with_typo_still_maps_to_identifier(self) -> None:
        query = _make_query("list all serial and part nmubers")
        assert inferer.infer(query) == RetrievalQueryIntent.IDENTIFIER

    def test_overview_intent_for_system_description_question(self) -> None:
        query = _make_query("What does the FWC system do?")
        assert inferer.infer(query) == RetrievalQueryIntent.OVERVIEW

    def test_identifier_presence_does_not_override_conceptual_question(self) -> None:
        query = RetrievalQuery(
            query_id="q_conceptual",
            query_text="What is the objective of commissioning the FWC12?",
            detected_identifiers=["fwc12"],
        )
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE

    def test_explicit_identifier_lookup_still_wins_when_identifier_is_present(self) -> None:
        query = RetrievalQuery(
            query_id="q_identifier",
            query_text="What does ordering code MK311007 mean?",
            detected_identifiers=["mk311007"],
        )
        assert inferer.infer(query) == RetrievalQueryIntent.IDENTIFIER

    def test_procedure_intent_for_start_run(self) -> None:
        query = _make_query("How do I start and run the macerator?")
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE

    def test_maintenance_tasks_map_to_maintenance(self) -> None:
        query = _make_query("What maintenance tasks are required for this document?")
        assert inferer.infer(query) == RetrievalQueryIntent.MAINTENANCE

    def test_procedure_intent_for_remove(self) -> None:
        query = _make_query("How do I remove the screen basket?")
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE

    def test_specification_intent_for_pressure(self) -> None:
        query = _make_query("What is the operating pressure range?")
        assert inferer.infer(query) == RetrievalQueryIntent.SPECIFICATION

    def test_table_intent_for_spare_parts(self) -> None:
        query = _make_query("Show me the spare parts table.")
        assert inferer.infer(query) == RetrievalQueryIntent.TABLE

    def test_none_query_returns_general(self) -> None:
        assert inferer.infer(None) == RetrievalQueryIntent.GENERAL

    def test_procedure_intent_for_replace(self) -> None:
        """'replace' is a PROCEDURE marker in the original inline check but
        was NOT in the shared _EXPLICIT_PROCEDURE_MARKERS list used only for
        the old maintenance veto -- regression guard against porting the
        wrong marker list when this was scored."""
        query = _make_query("How do I replace the drive belt?")
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE

    def test_lubricate_maps_to_maintenance_not_procedure(self) -> None:
        """'lubricate' is a PROCEDURE marker, but 'lubricat' (substring
        match) is ALSO a MAINTENANCE marker, and the original code's
        maintenance veto only checked a narrower marker list that excludes
        'lubricate' -- so this was MAINTENANCE in the original too, since
        MAINTENANCE is checked before PROCEDURE. Both intents score equally
        here (one marker hit each); the priority-rank tie-break (MAINTENANCE
        before PROCEDURE, matching the original scan order) reproduces it."""
        query = _make_query("How do I lubricate the bearing?")
        assert inferer.infer(query) == RetrievalQueryIntent.MAINTENANCE


# ---------------------------------------------------------------------------
# classify() scoring/gating internals: deliberate behavior changes and the
# tightest existing margin, verified via scores rather than just the winner.
# ---------------------------------------------------------------------------

class TestScoredClassification:
    def test_maintenance_signal_overwhelms_incidental_procedure_marker(self) -> None:
        """Deliberate behavior change from the original if/elif inferer:
        the original hard-vetoed MAINTENANCE entirely whenever ANY explicit
        procedure marker was present, regardless of how strong the
        maintenance signal was. The scored classifier instead requires
        MAINTENANCE to beat a competing PROCEDURE score by a larger gap
        (4, not the default 2) -- so an overwhelming maintenance signal
        with only one incidental procedure word still wins as MAINTENANCE
        rather than being forced to PROCEDURE."""
        query = _make_query(
            "What is the preventive maintenance schedule and maintenance "
            "interval for the belt, and what is the procedure?"
        )
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.MAINTENANCE
        assert classification.runner_up_intent == RetrievalQueryIntent.PROCEDURE
        assert classification.gap >= 4

    def test_table_vs_identifier_listing_combo_is_the_tightest_existing_margin(
        self,
    ) -> None:
        """'Show me the spare parts table.' scores TABLE=8 (two distinct
        marker hits: 'table' + 'spare part') against IDENTIFIER=6 (the
        verb+marker 'listing' combo: 'show' + 'part') -- a gap of exactly 2,
        the minimum required. This is the tightest margin found across the
        whole existing test suite; any future edit to the TABLE or
        IDENTIFIER marker lists should re-check this case since it could
        silently flip GENERAL or IDENTIFIER without changing this test."""
        query = _make_query("Show me the spare parts table.")
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.TABLE
        assert classification.score == 8
        assert classification.runner_up_intent == RetrievalQueryIntent.IDENTIFIER
        assert classification.runner_up_score == 6
        assert classification.gap == 2

    def test_classify_exposes_runner_up_for_close_scores(self) -> None:
        query = _make_query(
            "What are likely causes if the pump runs continuously?"
        )
        classification = inferer.classify(query)
        assert classification.intent == RetrievalQueryIntent.TROUBLESHOOTING
        assert classification.runner_up_intent == RetrievalQueryIntent.PROCEDURE
        assert classification.gap == 0

    def test_classify_reports_high_confidence_for_unambiguous_query(self) -> None:
        query = _make_query(
            "What are the likely causes and remedies for pump problems?"
        )
        classification = inferer.classify(query)
        assert classification.resolution_tier == "scored"
        assert classification.score == 8
        assert classification.runner_up_intent is None
        assert classification.confidence == 1.0

    def test_classify_reports_lower_confidence_for_single_weak_signal(self) -> None:
        query = _make_query("How do I troubleshoot the pump?")
        classification = inferer.classify(query)
        assert classification.score == 4
        assert classification.runner_up_intent is None
        assert classification.confidence == 0.75

    def test_classify_none_query_has_general_fallback_tier(self) -> None:
        classification = inferer.classify(None)
        assert classification.intent == RetrievalQueryIntent.GENERAL
        assert classification.resolution_tier == "general"
        assert classification.fallback_reason == "query_is_none"

    def test_infer_still_returns_bare_intent_for_backward_compatibility(self) -> None:
        query = _make_query("How do I troubleshoot the pump?")
        assert inferer.infer(query) == RetrievalQueryIntent.TROUBLESHOOTING


# ---------------------------------------------------------------------------
# resolve(): reads RetrievalQuery.detected_intent when the query was already
# analyzed, instead of re-running the classifier -- the mechanism that lets
# RetrievalWorkflow/QuestionAnsweringRouter/RetrievalContextExpander/
# DeterministicHybridReranker avoid redundant infer() calls on the same
# already-analyzed query object within one request.
# ---------------------------------------------------------------------------

class TestResolveAvoidsRedundantComputation:
    def test_resolve_computes_fresh_when_query_not_yet_analyzed(self) -> None:
        query = _make_query("This is a safety concern.")
        assert query.analyzed is False
        assert inferer.resolve(query) == RetrievalQueryIntent.SAFETY

    def test_resolve_reads_cached_value_instead_of_recomputing(self) -> None:
        query = _make_query("This is a safety concern.")
        query.analyzed = True
        query.detected_intent = "procedure"  # deliberately wrong vs. the text

        assert inferer.resolve(query) == RetrievalQueryIntent.PROCEDURE

    def test_resolve_falls_back_to_infer_when_analyzed_but_no_cached_value(
        self,
    ) -> None:
        query = _make_query("This is a safety concern.")
        query.analyzed = True
        assert query.detected_intent is None

        assert inferer.resolve(query) == RetrievalQueryIntent.SAFETY

    def test_resolve_matches_infer_after_a_real_analyze_call(self) -> None:
        from src.application.workflows.retrieval.retrieval_query_analyzer import (
            RetrievalQueryAnalyzer,
        )

        analyzer = RetrievalQueryAnalyzer()
        query = RetrievalQuery(query_id="q_test", query_text="This is a safety concern.")

        analyzed = analyzer.analyze(query)

        assert analyzed.detected_intent == RetrievalQueryIntent.SAFETY.value
        assert inferer.resolve(analyzed) == RetrievalQueryIntent.SAFETY

    def test_resolve_returns_general_for_none_query(self) -> None:
        assert inferer.resolve(None) == RetrievalQueryIntent.GENERAL


# ---------------------------------------------------------------------------
# Negation awareness: a marker preceded by a negation cue within a short
# lookback window no longer contributes to its intent's score.
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Comparative-query signal: exposed as a flag on the classification result,
# not a new RetrievalQueryIntent enum member (the parallel taxonomies don't
# have a clean comparative slot either).
# ---------------------------------------------------------------------------

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
