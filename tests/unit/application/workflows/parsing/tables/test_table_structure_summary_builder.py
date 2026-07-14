from src.application.workflows.parsing.tables.structure import (
    TableShape,
    TableStructureSummaryBuilder,
)


def test_builder_summarizes_maintenance_schedule_matrix() -> None:
    summary = TableStructureSummaryBuilder().build(
        [
            ["Task", "D", "W", "M", "Notes"],
            ["Inspect basket", "x", "", "x", "See annex"],
        ]
    )

    assert summary is not None
    assert summary.table_shape == TableShape.MAINTENANCE_SCHEDULE_MATRIX
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
        [
            ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
            ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ]
    )

    assert summary is not None
    assert summary.table_shape == TableShape.PERFORMANCE_CURVE_MATRIX
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
        [
            ["Parameter", "Compact version", "Remote version", "Unit"],
            ["Pressure range", "0...10", "0...16", "bar"],
            ["Output signal", "4-20 mA", "4-20 mA", "mA"],
        ]
    )

    assert summary is not None
    assert summary.table_shape == TableShape.SPECIFICATION_MATRIX
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
