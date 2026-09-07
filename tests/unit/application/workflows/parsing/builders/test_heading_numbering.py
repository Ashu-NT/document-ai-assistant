from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    extract_heading_number,
    has_structured_record_heading,
    strip_heading_number,
)


def test_heading_numbering_supports_trailing_manual_numbers() -> None:
    text = "Maintenance 7.1.11"

    assert extract_heading_number(text) == "7.1.11"
    assert strip_heading_number(text) == "Maintenance"


def test_heading_numbering_preserves_non_numbered_titles() -> None:
    text = "Manual Operation Page"

    assert extract_heading_number(text) is None
    assert strip_heading_number(text) == text


def test_structured_record_heading_accepts_catalog_codes_not_outline_numbers() -> None:
    assert has_structured_record_heading("3 - High temperature") is True
    assert has_structured_record_heading("641: System reset") is True
    assert has_structured_record_heading("7.2.3 Fault messages") is False
    assert has_structured_record_heading("3 Maintenance") is False
