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
