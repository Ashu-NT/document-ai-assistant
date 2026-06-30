"""
Tests for DOCUMENT_EXPLORATION intent detection via RetrievalQueryIntentInferer.

Detection runs before all other intents in the inferer, so any query whose
structure signals "what exists in this document" is classified as
DOCUMENT_EXPLORATION regardless of vocabulary that would otherwise match
TABLE, IDENTIFIER, SPECIFICATION, or PROCEDURE.
"""
import pytest

from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.workflows.retrieval.retrieval_query_intent_inferer import (
    RetrievalQueryIntentInferer,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


@pytest.fixture
def inferer() -> RetrievalQueryIntentInferer:
    return RetrievalQueryIntentInferer()


def _query(text: str, identifiers: list[str] | None = None) -> RetrievalQuery:
    return RetrievalQuery(
        query_id="q_test",
        query_text=text,
        detected_identifiers=identifiers or [],
    )


# ---------------------------------------------------------------------------
# Item 2 — "What information is in this PDF?"
# ---------------------------------------------------------------------------

def test_what_information_is_in_this_pdf(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What information is in this PDF?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Item 3 — "What sections are available?"
# ---------------------------------------------------------------------------

def test_what_sections_are_available(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What sections are available?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_sections_exist(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What sections exist?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Item 4 — "What identifiers are mentioned?"
# ---------------------------------------------------------------------------

def test_what_identifiers_are_mentioned(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What identifiers are mentioned?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_identifiers_are_present(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What identifiers are present?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_identifiers_are_listed_in_this_document(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What identifiers are listed in this document?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Item 5 — "What tables are available?"
# ---------------------------------------------------------------------------

def test_what_tables_are_available(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What tables are available?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Item 1 — DOCUMENT_EXPLORATION detected before other intents
# ---------------------------------------------------------------------------

def test_exploration_wins_over_table_intent(inferer: RetrievalQueryIntentInferer) -> None:
    # "table" appears in the TABLE marker list; exploration pattern runs first
    assert inferer.infer(_query("What tables are in this document?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_exploration_wins_over_identifier_intent_when_identifiers_detected(
    inferer: RetrievalQueryIntentInferer,
) -> None:
    # query.has_identifiers() would return True, but exploration check runs first
    query = _query(
        "What identifiers are listed in this document?",
        identifiers=["hp-001"],
    )
    assert inferer.infer(query) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_exploration_wins_over_identifier_chunk_type(inferer: RetrievalQueryIntentInferer) -> None:
    # SPARE_PARTS_TABLE chunk type would normally trigger TABLE; exploration wins
    query = RetrievalQuery(
        query_id="q_test",
        query_text="What tables are available in this document?",
        chunk_types=[ChunkType.SPARE_PARTS_TABLE],
    )
    assert inferer.infer(query) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_exploration_wins_over_procedure_markers(inferer: RetrievalQueryIntentInferer) -> None:
    # "list" appears in TABLE markers; "sections" exploration pattern runs first
    assert inferer.infer(_query("List sections")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Additional exploration patterns
# ---------------------------------------------------------------------------

def test_what_does_this_document_contain(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What does this document contain?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_does_this_manual_contain(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What does this manual contain?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_is_in_this_manual(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is in this manual?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_equipment_is_covered(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What equipment is covered?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_is_documented_here(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is documented here?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_is_this_manual_about(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is this manual about?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_document_structure(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("document structure")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_document_overview(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("document overview")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_show_sections(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("Show sections")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_can_i_find_in(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What can I find in this document?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_topics_are_covered(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What topics are covered?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


def test_what_figures_are_available(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What figures are available?")) == RetrievalQueryIntent.DOCUMENT_EXPLORATION


# ---------------------------------------------------------------------------
# Item 6 — Specific factual queries still map to their correct intent
# ---------------------------------------------------------------------------

def test_serial_number_query_maps_to_identifier(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is the serial number?")) == RetrievalQueryIntent.IDENTIFIER


def test_part_number_query_maps_to_identifier(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is the part number for the filter?")) == RetrievalQueryIntent.IDENTIFIER


def test_voltage_query_maps_to_specification(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What is the voltage?")) == RetrievalQueryIntent.SPECIFICATION


def test_start_pump_maps_to_procedure(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("How do I start the pump?")) == RetrievalQueryIntent.PROCEDURE


def test_maintenance_interval_maps_to_maintenance(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("How often should I lubricate the bearing?")) == RetrievalQueryIntent.MAINTENANCE


def test_troubleshooting_query_maps_to_troubleshooting(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("The pump is not working. What could be the fault?")) == RetrievalQueryIntent.TROUBLESHOOTING


def test_safety_query_maps_to_safety(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(_query("What safety warnings apply when changing the filter?")) == RetrievalQueryIntent.SAFETY


def test_none_query_maps_to_general(inferer: RetrievalQueryIntentInferer) -> None:
    assert inferer.infer(None) == RetrievalQueryIntent.GENERAL
