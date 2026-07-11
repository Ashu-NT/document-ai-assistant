from tests.unit.application.services.document._test_identifier_promotion_service_support import *  # noqa: F401,F403

def test_promote_multiple_extracted_identifiers():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="DRG-5001",
                identifier_type="drawing_number",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            ),
            ExtractedIdentifier(
                raw_value="ISO 9001",
                identifier_type="certificate_number",
                source_chunk_id="chunk_001",
                confidence_score=0.95,
            ),
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert IdentifierType.DRAWING_NUMBER in types
    assert IdentifierType.CERTIFICATE_NUMBER in types

def test_default_min_length_allows_short_values():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("A1")])
    identifiers = IdentifierPromotionService().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "A1"

def test_min_length_filters_out_short_normalized_values():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("A1")])
    service = IdentifierPromotionService(min_length=3)
    identifiers = service.promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_min_length_keeps_values_meeting_the_threshold():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("HP-001")])
    service = IdentifierPromotionService(min_length=3)
    identifiers = service.promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"
