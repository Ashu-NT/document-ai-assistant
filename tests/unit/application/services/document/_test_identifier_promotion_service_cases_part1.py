from tests.unit.application.services.document._test_identifier_promotion_service_support import *  # noqa: F401,F403

def test_promote_part_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("HP-001")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    id_ = identifiers[0]
    assert id_.identifier_type == IdentifierType.PART_NUMBER
    assert id_.raw_value == "HP-001"
    assert id_.normalized_value == "HP-001"
    assert id_.document_id == "doc_001"
    assert id_.chunk_id == "chunk_001"
    assert id_.confidence_score == 0.9

def test_promote_model_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number="HP-500")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.MODEL_NUMBER
    assert identifiers[0].raw_value == "HP-500"

def test_promote_contact_point_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(
        contact_points=[
            _make_contact_point(
                value="service@example.com",
                contact_type=ContactPointType.EMAIL_ADDRESS,
            )
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.EMAIL_ADDRESS
    assert identifiers[0].raw_value == "service@example.com"

def test_contact_point_dedupes_against_matching_extracted_identifier():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="extraction_001",
        document_id="doc_001",
        contact_points=[
            _make_contact_point(
                value="service@example.com",
                contact_type=ContactPointType.EMAIL_ADDRESS,
            )
        ],
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="service@example.com",
                identifier_type="email_address",
                source_chunk_id="chunk_001",
                confidence_score=0.8,
            )
        ],
    )

    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.EMAIL_ADDRESS

def test_promote_serial_number_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number=None, serial_number="SN-1234")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.SERIAL_NUMBER
    assert identifiers[0].raw_value == "SN-1234"

def test_promote_equipment_with_both_numbers_creates_two_identifiers():
    graph = _make_graph()
    extraction = _make_extraction(
        equipment=[_make_equipment(model_number="HP-500", serial_number="SN-1234")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert types == {IdentifierType.MODEL_NUMBER, IdentifierType.SERIAL_NUMBER}

def test_deduplication_skips_same_normalized_value_and_type():
    graph = _make_graph(chunk_ids=["chunk_001", "chunk_002"])
    extraction = _make_extraction(
        spare_parts=[
            _make_spare_part("HP-001", source_chunk_id="chunk_001"),
            _make_spare_part("hp-001", source_chunk_id="chunk_002"),  # same after normalize
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"

def test_deduplication_keeps_same_value_different_type():
    graph = _make_graph()
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001")],
        equipment=[_make_equipment(model_number="HP-001")],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert IdentifierType.PART_NUMBER in types
    assert IdentifierType.MODEL_NUMBER in types

def test_invalid_chunk_id_not_attached():
    graph = _make_graph(chunk_ids=["chunk_001"])
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", source_chunk_id="chunk_unknown")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].chunk_id is None

def test_no_source_chunk_id_produces_null_chunk_id():
    graph = _make_graph()
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", source_chunk_id=None)]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].chunk_id is None

def test_blank_part_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("   ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_none_part_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part(None)])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_none_model_number_skipped():
    graph = _make_graph()
    extraction = _make_extraction(equipment=[_make_equipment(model_number=None)])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_empty_extraction_produces_no_identifiers():
    graph = _make_graph()
    extraction = _make_extraction()
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_identifier_ids_are_unique():
    graph = _make_graph(chunk_ids=["chunk_001", "chunk_002"])
    extraction = _make_extraction(
        spare_parts=[
            _make_spare_part("HP-001", source_chunk_id="chunk_001"),
            _make_spare_part("HP-002", source_chunk_id="chunk_002"),
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    ids = [i.identifier_id for i in identifiers]
    assert len(ids) == len(set(ids))

def test_normalized_value_strips_and_uppercases():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part(" hp 001 ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].normalized_value == "HP001"
    assert identifiers[0].raw_value == "hp 001"

def test_raw_value_is_stripped_of_outer_whitespace():
    graph = _make_graph()
    extraction = _make_extraction(spare_parts=[_make_spare_part("  HP-001  ")])
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"

def test_document_id_is_taken_from_graph():
    graph = _make_graph(document_id="doc_XYZ")
    extraction = _make_extraction(
        spare_parts=[_make_spare_part("HP-001", document_id="doc_XYZ")],
        document_id="doc_XYZ",
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers[0].document_id == "doc_XYZ"

def test_promote_manufacturer_name_creates_identifier():
    graph = _make_graph()
    extraction = _make_extraction_with_manufacturers(
        manufacturers=[_make_manufacturer("Grundfos")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    id_ = identifiers[0]
    assert id_.identifier_type == IdentifierType.MANUFACTURER_NAME
    assert id_.raw_value == "Grundfos"
    assert id_.document_id == "doc_001"
    assert id_.confidence_score == 0.9

def test_blank_manufacturer_name_skipped():
    graph = _make_graph()
    extraction = _make_extraction_with_manufacturers(
        manufacturers=[_make_manufacturer("   ")]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []

def test_manufacturer_name_deduplication():
    graph = _make_graph(chunk_ids=["chunk_001", "chunk_002"])
    extraction = _make_extraction_with_manufacturers(
        manufacturers=[
            _make_manufacturer("Grundfos", source_chunk_id="chunk_001"),
            _make_manufacturer("grundfos", source_chunk_id="chunk_002"),
        ]
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "Grundfos"

def test_manufacturer_and_part_number_both_promoted():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        spare_parts=[_make_spare_part("HP-001")],
        manufacturers=[_make_manufacturer("Grundfos")],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 2
    types = {i.identifier_type for i in identifiers}
    assert IdentifierType.PART_NUMBER in types
    assert IdentifierType.MANUFACTURER_NAME in types

def test_promote_extracted_identifier_creates_identifier():
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
            )
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    id_ = identifiers[0]
    assert id_.identifier_type == IdentifierType.DRAWING_NUMBER
    assert id_.raw_value == "DRG-5001"
    assert id_.document_id == "doc_001"
    assert id_.chunk_id == "chunk_001"
    assert id_.confidence_score == 0.9
