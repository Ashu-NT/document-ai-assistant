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


def test_detects_curve_even_when_the_first_data_row_has_a_sparse_column() -> None:
    """Regression test: detection previously relied solely on the third
    row (the first data row) as the canonical sample - a single blank
    cell there (a sensor reading not taken at one flow point) sank
    detection for the whole table even when later rows were fully
    populated. A few candidate rows should be tried before giving up.
    """
    rows = [
        ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
        ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
        ["MXV 25-220C", "3", "4", "H m", "228", "", "202"],
        ["MXV 25-220C", "3", "4", "H m", "230", "215", "200"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is not None
    assert spec.metric_index == 3
    assert spec.data_start_index == 4


def test_does_not_detect_a_discrete_numeric_variant_axis_repeated_on_both_header_rows() -> None:
    """Regression test: a genuine curve axis point is the same physical
    value expressed in two different units (e.g. "1"/"16.6"), so at
    least one data column should show a real conversion between the two
    header rows. A spec table keyed by discrete numeric size codes (bolt
    diameters) that happen to repeat identically on both header rows -
    because there's no unit to convert - must not be misread as a curve.
    """
    rows = [
        ["Fastener", "Torque", "6", "8", "10", "12"],
        ["Fastener", "Nm", "6", "8", "10", "12"],
        ["Steel bolt", "", "5", "15", "30", "55"],
    ]

    spec = PerformanceCurveMatrixDetector().detect(rows)

    assert spec is None
