from src.application.workflows.question_answering.answer_context import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)


def test_entry_builds_single_reference_from_primary_source_when_absent() -> None:
    entry = AnswerMaintenanceEntry(
        task="Replace filter",
        interval="Every 500 hours",
        component="filter",
        notes=None,
        source_number=7,
    )

    assert entry.source_number == 7
    assert len(entry.references) == 1
    assert entry.references[0].source_number == 7
    assert entry.source_numbers == [7]


def test_entry_canonicalizes_primary_source_number_from_first_reference() -> None:
    entry = AnswerMaintenanceEntry(
        task="Replace filter",
        interval="Every 500 hours",
        component="filter",
        notes=None,
        source_number=99,
        references=[
            AnswerMaintenanceReference(
                source_number=3,
                page_start=12,
                page_end=13,
                section_path="Maintenance > Filters",
            ),
            AnswerMaintenanceReference(
                source_number=4,
                page_start=15,
                page_end=15,
                section_path="Maintenance > Spare Parts",
            ),
        ],
    )

    assert entry.source_number == 3
    assert entry.source_numbers == [3, 4]
    assert entry.page_start == 12
    assert entry.page_end == 13
    assert entry.section_path == "Maintenance > Filters"
    assert entry.section_paths == [
        "Maintenance > Filters",
        "Maintenance > Spare Parts",
    ]
