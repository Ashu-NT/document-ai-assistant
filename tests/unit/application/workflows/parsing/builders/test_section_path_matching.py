from src.application.workflows.parsing.builders.chunking.text.section_path_matching import (
    normalize_section_path_for_matching,
    normalized_section_path_text,
)


def test_normalize_section_path_for_matching_strips_numbering_but_keeps_labels() -> None:
    section_path = [
        "7 Components",
        "7.1 Macerators",
        "7.1.11 Maintenance",
    ]

    normalized = normalize_section_path_for_matching(section_path)

    assert normalized == [
        "Components",
        "Macerators",
        "Maintenance",
    ]


def test_normalize_section_path_for_matching_deduplicates_casefolded_segments() -> None:
    section_path = [
        "7 Maintenance",
        "Maintenance",
        "7.1 Filters",
    ]

    normalized = normalize_section_path_for_matching(section_path)

    assert normalized == ["Maintenance", "Filters"]


def test_normalized_section_path_text_joins_matching_path() -> None:
    section_path = [
        "7 Components",
        "7.2 Food Waste Press",
    ]

    assert normalized_section_path_text(section_path) == "Components > Food Waste Press"
