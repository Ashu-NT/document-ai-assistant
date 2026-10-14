from src.application.prompts.extraction import ExtractionPromptType
from src.application.workflows.extraction.candidates.extraction_cross_signal_detector import (
    ExtractionCrossSignalDetector,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


def make_chunk(**overrides) -> DocumentChunk:
    defaults = dict(
        chunk_id="chunk_001",
        document_id="document_001",
        section_id="section_001",
        content="",
        chunk_type=ChunkType.GENERAL,
        section_path=[],
        table_ids=[],
        source=SourceLocation(),
    )
    defaults.update(overrides)
    return DocumentChunk(**defaults)


def test_no_signals_for_plain_content() -> None:
    chunk = make_chunk(content="This page intentionally left blank.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert detected == frozenset()


def test_manufacturer_keyword_detected() -> None:
    chunk = make_chunk(content="This pump is manufactured by Acme Hydraulics.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.MANUFACTURER in detected


def test_manufacturer_suffix_regex_detected() -> None:
    chunk = make_chunk(content="Distributed under license from Muller GmbH.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.MANUFACTURER in detected


def test_supplier_keyword_detected() -> None:
    chunk = make_chunk(content="This part is supplied by FMD Rotterdam.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.SUPPLIER in detected


def test_contact_point_email_detected() -> None:
    chunk = make_chunk(content="For service support email info@example.com.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.CONTACT_POINT in detected


def test_contact_point_labeled_phone_detected() -> None:
    chunk = make_chunk(content="Tel: +49 40 1234 5678")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.CONTACT_POINT in detected


def test_part_number_regex_detected() -> None:
    chunk = make_chunk(content="Order replacement filter HP-001 from stock.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.SPARE_PART in detected


def test_spec_value_regex_detected() -> None:
    chunk = make_chunk(content="Supply voltage is rated at 230V, 50Hz.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.SPECIFICATION in detected


def test_interval_regex_detected() -> None:
    chunk = make_chunk(content="Replace the filter every 1000 hours.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.MAINTENANCE_INTERVAL in detected


def test_safety_content_marker_detected() -> None:
    chunk = make_chunk(content="Danger: disconnect power before servicing.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.SAFETY_WARNING in detected


def test_troubleshooting_content_marker_detected() -> None:
    chunk = make_chunk(
        content="Symptom: pump fails to start. Probable cause: blown fuse."
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.TROUBLESHOOTING in detected


def test_header_marker_detected_from_section_path() -> None:
    chunk = make_chunk(
        content="See table below.",
        section_path=["4", "Manufacturer"],
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.MANUFACTURER in detected


def test_contact_header_marker_detected_from_section_path() -> None:
    chunk = make_chunk(
        content="See manufacturer details below.",
        section_path=["8", "Contact Information"],
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.CONTACT_POINT in detected


def test_table_presence_bumps_spare_part_and_specification() -> None:
    chunk = make_chunk(content="Table contents.", table_ids=["table_001"])

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.SPARE_PART in detected
    assert ExtractionPromptType.SPECIFICATION in detected


def test_mtu_cover_page_equipment_phrase_detected() -> None:
    chunk = make_chunk(
        content=(
            "Marine engine-generator set with 20V4000M53B engine "
            "Application group 3B"
        )
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_equivalent_generator_set_with_code_expression_detected() -> None:
    chunk = make_chunk(content="Generator set with XY12345AB installed on site.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_equivalent_genset_model_expression_detected() -> None:
    chunk = make_chunk(content="Genset model AB987654 was commissioned in 2024.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_code_before_engine_noun_detected() -> None:
    chunk = make_chunk(content="The 20V4000M53B engine was inspected on site.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_differently_formatted_model_code_detected() -> None:
    chunk = make_chunk(content="Equipment model abc123xyz is installed here.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_certificate_number_near_engine_not_detected_as_equipment() -> None:
    chunk = make_chunk(
        content="Certificate No. SA18000AB was issued for this engine."
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_order_number_near_engine_not_detected_as_equipment() -> None:
    chunk = make_chunk(content="Order No. AB111777 engine spare kit shipped.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_document_reference_near_engine_not_detected_as_equipment() -> None:
    chunk = make_chunk(
        content="Document No. SA18000434E engine type approval record."
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_serial_number_near_engine_not_detected_as_equipment() -> None:
    chunk = make_chunk(content="Serial Number AB123456 fitted to the engine.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_spare_part_number_near_engine_not_detected_as_equipment() -> None:
    chunk = make_chunk(content="Spare part AB123456 for the engine is in stock.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_bare_alphanumeric_code_without_equipment_context_not_detected() -> None:
    chunk = make_chunk(content="Reference code AB123456XY appears in this document.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_generic_pump_model_expression_detected() -> None:
    chunk = make_chunk(content="Centrifugal pump with XR4500KL installed in bay 3.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_generic_motor_model_expression_detected() -> None:
    chunk = make_chunk(content="The QM2200AB motor drives the main conveyor.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_generic_compressor_model_expression_detected() -> None:
    chunk = make_chunk(content="Compressor with CP900XJ handles the air supply.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT in detected


def test_engine_keyword_without_any_model_code_not_detected() -> None:
    chunk = make_chunk(content="Check the engine oil level before starting.")

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.EQUIPMENT not in detected


def test_multiple_signals_can_be_detected_at_once() -> None:
    chunk = make_chunk(
        content=(
            "Manufactured by Acme Hydraulics GmbH. Replace filter HP-001 "
            "every 1000 hours. Supply voltage 230V."
        )
    )

    detected = ExtractionCrossSignalDetector().detect(chunk)

    assert ExtractionPromptType.MANUFACTURER in detected
    assert ExtractionPromptType.SPARE_PART in detected
    assert ExtractionPromptType.MAINTENANCE_INTERVAL in detected
    assert ExtractionPromptType.SPECIFICATION in detected
