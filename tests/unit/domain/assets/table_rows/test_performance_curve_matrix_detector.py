from src.domain.assets.table_rows.performance_curve_matrix_detector import (
    PerformanceCurveMatrixDetector,
)


def test_detects_performance_curve_matrix_with_dual_unit_axis_headers() -> None:
    rows = [
        ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
        ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
        ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is not None
    assert spec.descriptor_indexes == (0, 1, 2)
    assert spec.metric_index == 3
    assert spec.data_start_index == 4


def test_does_not_detect_specification_table_with_lettered_variant_columns() -> None:
    """Regression test: a dimension/spec table whose data columns are
    labeled variants (numeric size codes over lettered option codes) must
    not be misread as a performance curve matrix just because one of its
    two header rows happens to contain numbers.
    """
    rows = [
        ["Model", "Diameter", "100", "150", "200", "250"],
        ["Model", "mm", "A", "B", "C", "D"],
        ["Pump-X", "15.2", "12", "18", "24", "30"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is None


def test_does_not_detect_maintenance_interval_table_with_lettered_markers() -> None:
    rows = [
        ["Task", "Code", "100h", "250h", "500h", "1000h"],
        ["Task", "Code", "X", "Y", "Z", "W"],
        ["Check oil", "A1", "1", "0", "1", "1"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is None


def test_detects_curve_column_when_one_header_row_is_blank_from_a_merged_span() -> None:
    rows = [
        ["Pump type", "Motor power", "Q m3/h", "0", "1", "1.5"],
        ["Pump type", "kW", "", "", "", ""],
        ["MXV 25-220C", "3", "H m", "228", "213", "202"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is not None
    assert spec.metric_index == 2
    assert spec.data_start_index == 3
