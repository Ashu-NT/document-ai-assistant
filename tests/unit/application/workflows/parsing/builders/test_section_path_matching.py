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


def test_normalize_section_path_for_matching_prunes_safety_bridge_before_strong_branch() -> None:
    section_path = [
        "7 Components",
        "7.2 Food Waste Press",
        "Safety Precautions",
        "Owner / User Responsibility",
        "General Warnings:",
        "Electrical System Precautions",
        "Biohazard",
        "Food Waste Press Description",
        "Technical Data",
    ]

    normalized = normalize_section_path_for_matching(section_path)

    assert normalized == [
        "Components",
        "Food Waste Press",
        "Food Waste Press Description",
        "Technical Data",
    ]


def test_normalize_section_path_for_matching_prunes_overview_bridge_before_specific_tail() -> None:
    section_path = [
        "7 Components",
        "7.2 Food Waste Press",
        "Maintenance",
        "Overview & Maintenance Intervals",
        "Modifications to the Press",
        "Spare Parts",
        "Preventive Maintenance",
    ]

    normalized = normalize_section_path_for_matching(section_path)

    assert normalized == [
        "Components",
        "Food Waste Press",
        "Maintenance",
        "Spare Parts",
        "Preventive Maintenance",
    ]
