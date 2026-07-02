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
