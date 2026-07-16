from src.application.workflows.parsing.tables.structure.specification_matrix_structure_summarizer import (
    SpecificationMatrixStructureSummarizer,
)
from src.application.workflows.shared.table_shape import TableShape


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


def test_detects_a_spec_matrix_with_a_bare_single_letter_variant_column() -> None:
    """Regression test: a genuine spec/comparison table with a variant
    column literally named "A" (common in engineering drawings comparing
    options A/B/C) must not be excluded just because "a" happens to be
    a member of the maintenance-schedule single-letter set (D/W/M/Q/S/A)
    - that set is the right signal for a real schedule matrix, not for
    an incidental single-letter column name here.
    """
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Pump model", "A", "B", "C", "Weight"],
            ["Compact pump", "250", "180", "90", "12.5"],
            ["Standard pump", "300", "220", "110", "18.0"],
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


def test_does_not_detect_maintenance_interval_table_when_first_column_is_not_named_task() -> None:
    """Regression test grounded in a real ingested document: a
    maintenance-interval table whose first column is called
    "Description" rather than "Task" must still be excluded - the
    presence of a literal "Interval" column is enough on its own,
    regardless of what the first column happens to be named.
    """
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Description", "Interval", "Refers to"],
            ["Cleaning of the machine", "After daily use", ""],
            [
                "Check of the line strainer in the flush water pipe",
                "First time after a month use, then when needed",
                "",
            ],
            [
                "Preventive maintenance 1",
                "First time after 1 month use, then after 1 year, and 3 yearly from then on",
                "Check electrical connections.",
            ],
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


def test_does_not_detect_an_identity_record_with_qualified_header_variants() -> None:
    """Regression test grounded in a real ingested document: identity
    fields are commonly qualified ("Manufacturer Designation", "Serial
    Number") rather than used bare - an exact-header-equality check
    missed these variants entirely and let a genuine equipment
    certificate record slip through as a specification comparison.
    """
    summary = SpecificationMatrixStructureSummarizer().summarize(
        [
            ["Description", "Manufacturer Designation", "Serial Number", "IMO Number"],
            ["2 pcs., EC881-5", "L=500 mm, PN 350 bar", "SL060323", "0"],
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
