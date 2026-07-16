from src.application.workflows.retrieval.retrieval_query_intent import (
    RetrievalQueryIntent,
)
from src.application.prompts.extraction.common.extraction_prompt_type import (
    ExtractionPromptType,
)
from src.application.workflows.retrieval.structured.structured_evidence_query_analyzer import (
    StructuredEvidenceQueryAnalyzer,
)


def test_analyze_maps_maintenance_intent_to_maintenance_entity_types() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(
        query_text="how do I service the pump",
        intent=RetrievalQueryIntent.MAINTENANCE.value,
    )

    assert ExtractionPromptType.MAINTENANCE_TASK in analysis.entity_types
    assert ExtractionPromptType.MAINTENANCE_INTERVAL in analysis.entity_types
    assert ExtractionPromptType.PROCEDURE in analysis.entity_types


def test_analyze_maps_procedure_troubleshooting_and_specification_intents() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    procedure_analysis = analyzer.analyze(
        query_text="",
        intent=RetrievalQueryIntent.PROCEDURE.value,
    )
    troubleshooting_analysis = analyzer.analyze(
        query_text="",
        intent=RetrievalQueryIntent.TROUBLESHOOTING.value,
    )
    specification_analysis = analyzer.analyze(
        query_text="",
        intent=RetrievalQueryIntent.SPECIFICATION.value,
    )

    assert procedure_analysis.entity_types == [ExtractionPromptType.PROCEDURE]
    assert troubleshooting_analysis.entity_types == [
        ExtractionPromptType.TROUBLESHOOTING
    ]
    assert specification_analysis.entity_types == [
        ExtractionPromptType.SPECIFICATION,
        ExtractionPromptType.EQUIPMENT,
    ]


def test_analyze_ignores_unrecognized_intent_values_instead_of_matching_a_dead_branch() -> None:
    """Regression test: analyze() used to have an
    `elif intent == "certification":` branch that could never match, since
    RetrievalQueryIntent (the enum that actually populates detected_intent)
    has no CERTIFICATION member. Confirms an unrecognized intent string is
    now a documented no-op on the intent-branch rather than a silent,
    permanently-unreachable case."""
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(query_text="what is on this page", intent="certification")

    assert analysis.entity_types == []


def test_analyze_detects_manufacturer_keyword_without_intent() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(query_text="who is the manufacturer of the pump?")

    assert ExtractionPromptType.MANUFACTURER in analysis.entity_types


def test_analyze_detects_detail_entity_type_with_contact_point() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(
        query_text="what is the manufacturer's email address?"
    )

    assert analysis.detail_entity_type == ExtractionPromptType.MANUFACTURER
    assert ExtractionPromptType.CONTACT_POINT in analysis.entity_types


def test_analyze_extends_entity_types_when_identifiers_detected() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(
        query_text="what is MK311007",
        detected_identifiers=["mk311007"],
    )

    assert ExtractionPromptType.SPARE_PART in analysis.entity_types
    assert ExtractionPromptType.EQUIPMENT in analysis.entity_types
    assert ExtractionPromptType.SPECIFICATION in analysis.entity_types


def test_analyze_reports_wants_identifier_inventory_for_listing_queries() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(query_text="list all part numbers")

    assert analysis.wants_identifier_inventory is True
    assert analysis.identifier_types


def test_analyze_deduplicates_entity_types_while_preserving_order() -> None:
    analyzer = StructuredEvidenceQueryAnalyzer()

    analysis = analyzer.analyze(
        query_text="what is the specification for the equipment?",
        intent=RetrievalQueryIntent.SPECIFICATION.value,
    )

    assert analysis.entity_types.count(ExtractionPromptType.SPECIFICATION) == 1
    assert analysis.entity_types.count(ExtractionPromptType.EQUIPMENT) == 1
