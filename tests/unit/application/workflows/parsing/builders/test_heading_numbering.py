from src.application.workflows.parsing.builders.section_hierarchy.heading_numbering import (
    extract_heading_number,
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
