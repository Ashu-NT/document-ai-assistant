from tests.unit.application.services.document._test_identifier_promotion_service_support import *  # noqa: F401,F403

def test_promote_extracted_identifier_unknown_type_falls_back():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="XYZ-999",
                identifier_type="not_a_real_type",
                source_chunk_id="chunk_001",
                confidence_score=0.7,
            )
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.UNKNOWN

def test_promote_extracted_identifier_unknown_type_logs_warning(caplog):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="XYZ-999",
                identifier_type="not_a_real_type",
                source_chunk_id="chunk_001",
                confidence_score=0.7,
            )
        ],
    )
    with caplog.at_level("WARNING"):
        _service().promote(extraction, graph, IdGenerator())

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "not_a_real_type" in message
    assert "XYZ-999" in message
    assert "doc_001" in message

def test_promote_known_extracted_identifier_type_does_not_log_warning(caplog):
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
    with caplog.at_level("WARNING"):
        _service().promote(extraction, graph, IdGenerator())

    assert caplog.records == []

@pytest.mark.parametrize(
    ("raw_identifier_type", "expected_identifier_type"),
    [
        ("item_number", IdentifierType.COMPONENT_CODE),
        ("item_no", IdentifierType.COMPONENT_CODE),
        ("order_no", IdentifierType.COMPONENT_CODE),
        ("tag_no", IdentifierType.COMPONENT_CODE),
        ("part_no", IdentifierType.PART_NUMBER),
        ("serial_no", IdentifierType.SERIAL_NUMBER),
        ("model_no", IdentifierType.MODEL_NUMBER),
        ("product_name", IdentifierType.PRODUCT_NAME),
        ("equipment_name", IdentifierType.PRODUCT_NAME),
        ("dwg_no", IdentifierType.DRAWING_NUMBER),
        ("cert_no", IdentifierType.CERTIFICATE_NUMBER),
        ("vendor", IdentifierType.SUPPLIER_NAME),
    ],
)
def test_promote_extracted_identifier_alias_type_normalizes_to_known_enum(
    raw_identifier_type: str,
    expected_identifier_type: IdentifierType,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="ABC-123",
                identifier_type=raw_identifier_type,
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == expected_identifier_type

def test_promote_extracted_identifier_alias_type_does_not_log_warning(caplog):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="22W02466",
                identifier_type="item_number",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.COMPONENT_CODE
    assert caplog.records == []

def test_promote_product_name_identifier_does_not_log_warning(caplog):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="B-Control II control system",
                identifier_type="product_name",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == IdentifierType.PRODUCT_NAME
    assert identifiers[0].raw_value == "B-Control II control system"
    assert caplog.records == []

@pytest.mark.parametrize(
    ("raw_identifier_type", "raw_value", "expected_identifier_type"),
    [
        ("tel", "+33 493 742929", IdentifierType.PHONE_NUMBER),
        ("telephone_number", "+33 493 748062", IdentifierType.PHONE_NUMBER),
        ("email_address", "info@hemwater.com", IdentifierType.EMAIL_ADDRESS),
        ("url", "www.hemwater.com", IdentifierType.URL),
    ],
)
def test_promote_extracted_identifier_promotes_contact_style_metadata_without_warning(
    raw_identifier_type: str,
    raw_value: str,
    expected_identifier_type: IdentifierType,
    caplog,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value=raw_value,
                identifier_type=raw_identifier_type,
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].identifier_type == expected_identifier_type
    assert identifiers[0].raw_value == raw_value
    assert caplog.records == []

@pytest.mark.parametrize(
    ("raw_identifier_type", "raw_value"),
    [
        ("menu_name", "DIAGNOSTICS"),
        ("chapter_number", "81022"),
        ("parameter_value", "Pressure rating"),
    ],
)
def test_promote_extracted_identifier_ignores_non_identifier_metadata_without_warning(
    raw_identifier_type: str,
    raw_value: str,
    caplog,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value=raw_value,
                identifier_type=raw_identifier_type,
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_ignores_internal_chunk_id_without_warning(caplog):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="chunk_2f914a1d29194505ad08dce828fa0a3c",
                identifier_type="chunk_id",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_ignores_echoed_source_chunk_id_without_warning(
    caplog,
):
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="chunk_001",
                identifier_type="unknown",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )

    with caplog.at_level("WARNING"):
        identifiers = _service().promote(extraction, graph, IdGenerator())

    assert identifiers == []
    assert caplog.records == []

def test_promote_extracted_identifier_deduped_against_structured():
    graph = _make_graph()
    extraction = ExtractionResult(
        extraction_id="e001",
        document_id="doc_001",
        spare_parts=[_make_spare_part("HP-001")],
        extracted_identifiers=[
            ExtractedIdentifier(
                raw_value="HP-001",
                identifier_type="part_number",
                source_chunk_id="chunk_001",
                confidence_score=0.9,
            )
        ],
    )
    identifiers = _service().promote(extraction, graph, IdGenerator())

    assert len(identifiers) == 1
    assert identifiers[0].raw_value == "HP-001"
