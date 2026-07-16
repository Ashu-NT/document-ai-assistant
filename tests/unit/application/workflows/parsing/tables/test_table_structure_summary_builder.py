from src.application.workflows.parsing.tables.structure import (
    TableStructureSummaryBuilder,
)
from src.application.workflows.shared.table_kind import TableKind
from src.domain.assets import TableAsset


def _make_table(rows: list[list[str]]) -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="table",
        rows=rows,
        column_count=max((len(row) for row in rows), default=0),
    )


def test_builder_summarizes_maintenance_schedule_matrix() -> None:
    summary = TableStructureSummaryBuilder().build(
        _make_table(
            [
            ["Task", "D", "W", "M", "Notes"],
            ["Inspect basket", "x", "", "x", "See annex"],
            ]
        )
    )

    assert summary is not None
    assert summary.table_shape == TableKind.MAINTENANCE_SCHEDULE_MATRIX
    assert summary.header_paths == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
        ["Notes"],
    ]
    assert summary.axis_summary == {
        "row_axis": "task",
        "column_axis": "interval",
        "value_axis": "marker",
        "descriptor_axis": "notes",
    }
    assert summary.quality_score >= 0.8


def test_builder_summarizes_performance_curve_matrix() -> None:
    summary = TableStructureSummaryBuilder().build(
        _make_table(
            [
            ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
            ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
            ]
        )
    )

    assert summary is not None
    assert summary.table_shape == TableKind.PERFORMANCE_CURVE_MATRIX
    assert summary.header_paths == [
        ["Pump type"],
        ["Motor power", "kW"],
        ["Motor power", "HP"],
        ["Curve metric"],
        ["Q m3/h 0", "Q l/min 0"],
        ["Q m3/h 1", "Q l/min 16.6"],
        ["Q m3/h 1.5", "Q l/min 25"],
    ]
    assert summary.axis_summary == {
        "row_axis": "series",
        "column_axis": "curve_point",
        "value_axis": "numeric_measurement",
        "descriptor_axis": "curve_metric",
    }
    assert summary.quality_score >= 0.8


def test_builder_summarizes_specification_matrix() -> None:
    summary = TableStructureSummaryBuilder().build(
        _make_table(
            [
            ["Parameter", "Compact version", "Remote version", "Unit"],
            ["Pressure range", "0...10", "0...16", "bar"],
            ["Output signal", "4-20 mA", "4-20 mA", "mA"],
            ]
        )
    )

    assert summary is not None
    assert summary.table_shape == TableKind.SPECIFICATION_MATRIX
    assert summary.header_paths == [
        ["Parameter"],
        ["Field", "Compact version"],
        ["Field", "Remote version"],
        ["Unit"],
    ]
    assert summary.axis_summary == {
        "row_axis": "parameter",
        "column_axis": "field",
        "value_axis": "specification_value",
        "descriptor_axis": "unit",
    }
    assert summary.quality_score >= 0.7


def test_builder_falls_back_to_generic_record_table_summary() -> None:
    summary = TableStructureSummaryBuilder().build(
        _make_table(
            [
                ["Technical data", "", ""],
                ["Component", "Manufacturer", "Serial number"],
                ["Pump", "Calpeda", "SN-001"],
            ]
        )
    )

    assert summary is not None
    assert summary.table_shape == TableKind.RECORD_TABLE
    assert summary.header_paths == [
        ["component"],
        ["manufacturer"],
        ["serial number"],
    ]
    assert summary.axis_summary == {
        "row_axis": "record",
        "column_axis": "attribute",
        "value_axis": "cell_value",
    }
    assert summary.quality_score >= 0.6
