import pytest

from src.application.workflows.parsing.tables.structure.maintenance_schedule_structure_summarizer import (
    MaintenanceScheduleStructureSummarizer,
)
from src.application.workflows.shared.table_kind import TableKind


def test_summarize_returns_none_when_not_a_maintenance_interval_matrix() -> None:
    rows = [
        ["Task", "Description"],
        ["Inspect filter", "Check for debris"],
    ]

    assert MaintenanceScheduleStructureSummarizer().summarize(rows) is None


def test_summarize_produces_maintenance_schedule_matrix_summary() -> None:
    rows = [
        ["Task", "D", "W", "M"],
        ["Inspect filter", "x", "", ""],
        ["Replace gasket", "", "x", ""],
    ]

    summary = MaintenanceScheduleStructureSummarizer().summarize(rows)

    assert summary is not None
    assert summary.table_shape == TableKind.MAINTENANCE_SCHEDULE_MATRIX
    assert summary.header_paths == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
    ]
    assert summary.axis_summary == {
        "row_axis": "task",
        "column_axis": "interval",
        "value_axis": "marker",
    }
    assert summary.quality_score == pytest.approx(0.95)


def test_summarize_adds_descriptor_axis_when_a_notes_column_is_present() -> None:
    rows = [
        ["Task", "D", "W", "M", "Notes"],
        ["Inspect filter", "x", "", "", "Check monthly for wear"],
        ["Replace gasket", "", "x", "", "Use OEM parts"],
    ]

    summary = MaintenanceScheduleStructureSummarizer().summarize(rows)

    assert summary is not None
    assert summary.header_paths[-1] == ["Notes"]
    assert summary.axis_summary["descriptor_axis"] == "notes"
