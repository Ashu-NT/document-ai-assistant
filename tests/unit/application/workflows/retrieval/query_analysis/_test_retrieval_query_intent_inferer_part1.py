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
