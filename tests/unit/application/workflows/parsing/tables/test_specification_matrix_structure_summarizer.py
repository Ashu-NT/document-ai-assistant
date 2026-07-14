from src.application.workflows.parsing.tables.structure.specification_matrix_structure_summarizer import (
    SpecificationMatrixStructureSummarizer,
)
from src.application.workflows.parsing.tables.structure.table_shape import TableShape


def test_detects_genuine_specification_comparison_matrix() -> None:
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Parameter", "Compact version", "Remote version", "Unit"],
            ["Pressure range", "0...10", "0...16", "bar"],
            ["Output signal", "4-20 mA", "4-20 mA", "mA"],
        ]
    )

    assert summary is not None
    assert summary.table_shape == TableShape.SPECIFICATION_MATRIX


def test_does_not_detect_maintenance_narrative_table_with_free_text_intervals() -> None:
    """Regression test: a "Task | Interval | Notes" table with free-text
    interval descriptions (not boolean schedule markers) belongs to the
    maintenance-schedule family and must not be misread as a generic
    specification/parameter comparison matrix.
    """
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Task", "Interval", "Notes"],
            ["Check oil level", "Every 6 months", "See gearbox annex"],
            ["Replace filter", "Every 12 months", "Use OEM part"],
            ["Inspect belts", "Every 3 months", ""],
        ]
    )

    assert summary is None


def test_does_not_detect_equipment_identity_record_listing() -> None:
    """Regression test: a listing of distinct pieces of equipment
    identified by manufacturer/serial/location fields is a record table,
    not a parameter/value specification comparison.
    """
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Manufacturer", "Model", "Serial Number", "Location"],
            ["Siemens", "S7-1200", "SN-88213", "Panel A"],
            ["ABB", "ACS880", "SN-99123", "Panel B"],
        ]
    )

    assert summary is None


def test_does_not_detect_spare_parts_table() -> None:
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Position", "Description", "Qty", "Part Number"],
            ["70.00", "Lantern bracket", "1", "AB-123"],
            ["14.04", "Plug (filling)", "2", "CD-456"],
        ]
    )

    assert summary is None
