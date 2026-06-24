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
        # "what does" triggers IDENTIFIER intent, so use a different phrasing
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
    def test_procedure_intent_for_start_run(self) -> None:
        query = _make_query("How do I start and run the macerator?")
        assert inferer.infer(query) == RetrievalQueryIntent.PROCEDURE

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
