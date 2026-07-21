from src.application.workflows.retrieval.query_analysis.retrieval_query_chunk_type_preference_mapper import (
    RetrievalQueryChunkTypePreferenceMapper,
)
from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievalQuery


def _query(text: str = "") -> RetrievalQuery:
    return RetrievalQuery(query_id="q_001", query_text=text)


def _map(text: str, intent: RetrievalQueryIntent) -> list[ChunkType]:
    return RetrievalQueryChunkTypePreferenceMapper().map(query=_query(text), intent=intent)


# --- MAINTENANCE intent — the P1#5 regression surface ---------------------------
#
# outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md
# traced a real bug where maintenance-interval questions leaked
# ChunkType.TECHNICAL_SPECIFICATION into the preference list. Verified against
# current code (2026-07-02) that this branch no longer includes it in either
# variant; these tests lock that in so it can't silently regress.

def test_maintenance_intent_never_includes_technical_specification_without_interval_wording():
    preferences = _map("What maintenance tasks are required?", RetrievalQueryIntent.MAINTENANCE)

    assert ChunkType.TECHNICAL_SPECIFICATION not in preferences


def test_maintenance_intent_never_includes_technical_specification_with_interval_wording():
    preferences = _map("What are the maintenance intervals?", RetrievalQueryIntent.MAINTENANCE)

    assert ChunkType.TECHNICAL_SPECIFICATION not in preferences


def test_maintenance_intent_base_preference_order():
    preferences = _map("What maintenance tasks are required?", RetrievalQueryIntent.MAINTENANCE)

    assert preferences == [
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.SAFETY_WARNING,
        ChunkType.GENERAL,
        ChunkType.OVERVIEW,
    ]


def test_maintenance_intent_narrows_to_interval_and_table_when_interval_wording_present():
    preferences = _map("What are the maintenance intervals?", RetrievalQueryIntent.MAINTENANCE)

    assert preferences == [
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.GENERAL,
        ChunkType.OVERVIEW,
    ]
    # MAINTENANCE_INTERVAL and SPARE_PARTS_TABLE (the "table" category) lead —
    # this is the "MAINTENANCE_LOOKUP plus TABLE_LOOKUP" outcome the debug
    # report called for, without ever touching SAFETY_WARNING/spec content.


def test_maintenance_intent_narrows_for_schedule_wording():
    preferences = _map(
        "Is there a maintenance schedule for this equipment?", RetrievalQueryIntent.MAINTENANCE
    )

    assert preferences[:2] == [ChunkType.MAINTENANCE_INTERVAL, ChunkType.SPARE_PARTS_TABLE]


def test_maintenance_intent_narrows_for_service_interval_wording():
    preferences = _map(
        "What are the service intervals for this equipment?",
        RetrievalQueryIntent.MAINTENANCE,
    )

    assert preferences[:2] == [ChunkType.MAINTENANCE_INTERVAL, ChunkType.SPARE_PARTS_TABLE]


def test_maintenance_intent_narrows_for_how_often_wording():
    preferences = _map(
        "How often should the filter be replaced?", RetrievalQueryIntent.MAINTENANCE
    )

    assert preferences[:2] == [ChunkType.MAINTENANCE_INTERVAL, ChunkType.SPARE_PARTS_TABLE]


# --- IDENTIFIER intent -----------------------------------------------------------

def test_identifier_intent_base_preference_order():
    preferences = _map("What is the part number?", RetrievalQueryIntent.IDENTIFIER)

    assert preferences == [
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.CERTIFICATION_INFO,
        ChunkType.DRAWING_REFERENCE,
        ChunkType.GENERAL,
    ]


def test_identifier_intent_promotes_certification_for_certificate_wording():
    preferences = _map(
        "What is the certificate number for this component?", RetrievalQueryIntent.IDENTIFIER
    )

    assert preferences[0] == ChunkType.CERTIFICATION_INFO
    # promoted, not duplicated
    assert preferences.count(ChunkType.CERTIFICATION_INFO) == 1


def test_identifier_intent_promotes_certification_for_atex_wording():
    preferences = _map("What is the ATEX approval identifier?", RetrievalQueryIntent.IDENTIFIER)

    assert preferences[0] == ChunkType.CERTIFICATION_INFO


def test_identifier_intent_promotes_drawing_reference_for_a_typed_drawing_number():
    # extract_typed() requires a value matching its generic identifier
    # pattern (a digit group needs a separator, or a leading letter) --
    # "4471-2" qualifies, a bare "4471" would not.
    preferences = _map(
        "What is drawing no. 4471-2 for?", RetrievalQueryIntent.IDENTIFIER
    )

    assert preferences[0] == ChunkType.DRAWING_REFERENCE
    assert preferences.count(ChunkType.DRAWING_REFERENCE) == 1


def test_identifier_intent_promotes_technical_specification_for_a_typed_serial_number():
    preferences = _map("What is serial no. HP-001?", RetrievalQueryIntent.IDENTIFIER)

    assert preferences[0] == ChunkType.TECHNICAL_SPECIFICATION


def test_identifier_intent_typed_certificate_number_combines_with_certification_wording_promotion():
    preferences = _map(
        "What is cert no. 4471-2?", RetrievalQueryIntent.IDENTIFIER
    )

    assert preferences[0] == ChunkType.CERTIFICATION_INFO
    assert preferences.count(ChunkType.CERTIFICATION_INFO) == 1


# --- TABLE intent ------------------------------------------------------------------

def test_table_intent_preference_order():
    preferences = _map("Show me the spare parts table.", RetrievalQueryIntent.TABLE)

    assert preferences == [
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.CERTIFICATION_INFO,
        ChunkType.GENERAL,
    ]


# --- SPECIFICATION intent ----------------------------------------------------------

def test_specification_intent_base_preference_order():
    preferences = _map(
        "What is the operating temperature?", RetrievalQueryIntent.SPECIFICATION
    )

    assert preferences == [
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.CERTIFICATION_INFO,
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.GENERAL,
        ChunkType.SPARE_PARTS_TABLE,
    ]


def test_specification_intent_promotes_certification_for_certificate_wording():
    preferences = _map(
        "What is the certificate rating?", RetrievalQueryIntent.SPECIFICATION
    )

    assert preferences[0] == ChunkType.CERTIFICATION_INFO
    assert preferences.count(ChunkType.CERTIFICATION_INFO) == 1


def test_specification_intent_promotes_operation_instruction_for_pressure_setting_wording():
    preferences = _map(
        "How do I adjust the pressure setting?", RetrievalQueryIntent.SPECIFICATION
    )

    assert preferences[1] == ChunkType.OPERATION_INSTRUCTION


# --- PROCEDURE intent ----------------------------------------------------------------

def test_procedure_intent_base_preference_order():
    preferences = _map("How do I operate this valve?", RetrievalQueryIntent.PROCEDURE)

    assert preferences == [
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.TROUBLESHOOTING,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.SAFETY_WARNING,
        ChunkType.GENERAL,
        ChunkType.OVERVIEW,
    ]


def test_procedure_intent_narrows_for_interval_wording():
    preferences = _map(
        "What tasks are required on a lubrication interval basis?",
        RetrievalQueryIntent.PROCEDURE,
    )

    assert preferences == [
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.TROUBLESHOOTING,
        ChunkType.GENERAL,
        ChunkType.OVERVIEW,
    ]


def test_procedure_intent_narrows_for_commissioning_wording():
    preferences = _map(
        "What is the objective of the commissioning procedure?", RetrievalQueryIntent.PROCEDURE
    )

    assert preferences == [
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.GENERAL,
        ChunkType.OVERVIEW,
    ]


def test_procedure_intent_interval_wording_takes_precedence_over_commissioning_wording():
    preferences = _map(
        "How often should the installation be inspected on an interval basis?",
        RetrievalQueryIntent.PROCEDURE,
    )

    assert preferences[0] == ChunkType.MAINTENANCE_INTERVAL


# --- TROUBLESHOOTING / SAFETY / FIGURE / OVERVIEW / DOCUMENT_EXPLORATION --------

def test_troubleshooting_intent_preference_order():
    preferences = _map("The pump will not start.", RetrievalQueryIntent.TROUBLESHOOTING)

    assert preferences == [
        ChunkType.TROUBLESHOOTING,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.GENERAL,
    ]


def test_safety_intent_preference_order():
    preferences = _map("What are the safety warnings?", RetrievalQueryIntent.SAFETY)

    assert preferences == [
        ChunkType.SAFETY_WARNING,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.TROUBLESHOOTING,
        ChunkType.GENERAL,
    ]


def test_figure_intent_preference_order():
    preferences = _map("Show me the drawing.", RetrievalQueryIntent.FIGURE)

    assert preferences == [
        ChunkType.DRAWING_REFERENCE,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.GENERAL,
    ]


def test_overview_intent_preference_order():
    preferences = _map("Give me an overview of this document.", RetrievalQueryIntent.OVERVIEW)

    assert preferences == [
        ChunkType.OVERVIEW,
        ChunkType.GENERAL,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.TECHNICAL_SPECIFICATION,
    ]


def test_document_exploration_intent_safety_net():
    preferences = _map("List all documents.", RetrievalQueryIntent.DOCUMENT_EXPLORATION)

    assert preferences == [ChunkType.OVERVIEW, ChunkType.GENERAL]


# --- fallback / unmapped intents ---------------------------------------------------

def test_unmapped_intent_falls_back_to_existing_query_chunk_types():
    query = _query("Tell me something useful.")
    query.chunk_types = [ChunkType.GENERAL, ChunkType.OVERVIEW]

    preferences = RetrievalQueryChunkTypePreferenceMapper().map(
        query=query,
        intent=RetrievalQueryIntent.GENERAL,
    )

    assert preferences == [ChunkType.GENERAL, ChunkType.OVERVIEW]


def test_unmapped_intent_with_no_existing_chunk_types_returns_empty_list():
    preferences = _map("Tell me something useful.", RetrievalQueryIntent.GENERAL)

    assert preferences == []
