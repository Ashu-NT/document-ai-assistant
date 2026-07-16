from src.application.workflows.parsing.tables.normalization import (
    TableRowSemanticNormalizer,
)
from src.domain.assets import TableAsset, TableCellSpan


def test_normalize_rewrites_troubleshooting_rows_into_persistable_grid() -> None:
    table = TableAsset(
        table_id="table_1",
        document_id="doc_1",
        markdown="troubleshooting",
        table_category="troubleshooting_table",
        rows=[
            ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
            [
                "(6) Leakage from the mechanical seal",
                "6a)",
                "The mechanical seal has been",
                "6a)",
                "Replace the mechanical seal.",
            ],
            [
                "(6) Leakage from the mechanical seal",
                "6b)",
                "run dry or has stuck",
                "6b)",
                "Replace the mechanical seal.",
            ],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.rows == [
        ["Symptom", "Cause", "Remedy"],
        [
            "(6) Leakage from the mechanical seal",
            "The mechanical seal has been run dry or has stuck",
            "Replace the mechanical seal.",
        ],
    ]
    assert table.row_count == 2
    assert table.column_count == 3


def test_normalize_rewrites_parallel_streams_and_combines_matching_headers() -> None:
    table = TableAsset(
        table_id="table_2",
        document_id="doc_1",
        markdown="spare parts",
        table_category="spare_parts_table",
        rows=[
            ["Part Pos.", "Qty Unit", "Designation"],
            ["5040 4", "Pce", "spring washer"],
            ["7000 2", "Pce", "seal housing"],
        ],
        parallel_stream_rows=[
            [
                ["Part Pos.", "Qty Unit", "Designation"],
                ["5040 4", "Pce", "spring washer"],
            ],
            [
                ["Part Pos.", "Qty Unit", "Designation"],
                ["7000 2", "Pce", "seal housing"],
            ],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.parallel_stream_rows == [
        [["Position", "Quantity", "Unit", "Description"], ["5040", "4", "Pce", "spring washer"]],
        [["Position", "Quantity", "Unit", "Description"], ["7000", "2", "Pce", "seal housing"]],
    ]
    assert table.rows == [
        ["Position", "Quantity", "Unit", "Description"],
        ["5040", "4", "Pce", "spring washer"],
        ["7000", "2", "Pce", "seal housing"],
    ]


def test_normalize_leaves_unrelated_table_categories_untouched() -> None:
    table = TableAsset(
        table_id="table_3",
        document_id="doc_1",
        markdown="specs",
        table_category="technical_data_table",
        rows=[
            ["Parameter", "Value"],
            ["Voltage", "400V"],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is False
    assert table.rows == [
        ["Parameter", "Value"],
        ["Voltage", "400V"],
    ]


def test_normalize_rewrites_compact_schedule_matrix_via_maintenance_normalizer() -> None:
    table = TableAsset(
        table_id="table_4",
        document_id="doc_1",
        markdown="maintenance schedule",
        table_category="maintenance_interval_table",
        rows=[
            ["D", "Q Q", "M S A", "Task Reference"],
            ["X", "General visual inspection"],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.rows == [
        ["Daily", "Quarterly", "Monthly", "Semi-Annual", "Annual", "Task", "Notes"],
        ["x", "", "", "", "", "General visual inspection", ""],
    ]


def test_normalize_rewrites_wrapped_specification_rows_via_key_value_normalizer() -> None:
    table = TableAsset(
        table_id="table_5",
        document_id="doc_1",
        markdown="specs",
        table_category="technical_data_table",
        rows=[
            ["Model", "XV2000", "Speed", "1450 RPM"],
            ["Weight", "120 kg", "Diameter", "250 mm"],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.rows == [
        ["Label", "Value"],
        ["Model", "XV2000"],
        ["Speed", "1450 RPM"],
        ["Weight", "120 kg"],
        ["Diameter", "250 mm"],
    ]


def test_normalize_rewrites_performance_curve_rows_for_persistence() -> None:
    table = TableAsset(
        table_id="table_6",
        document_id="doc_1",
        markdown="curve",
        table_category="technical_data_table",
        rows=[
            ["Pump type", "Motor power", "Motor power", "Q m3/h", "0", "1", "1.5"],
            ["Pump type", "kW", "HP", "Q l/min", "0", "16.6", "25"],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.rows == [
        [
            "Pump type",
            "Motor power (kW)",
            "Motor power (HP)",
            "Curve metric",
            "Q m3/h 0 / Q l/min 0",
            "Q m3/h 1 / Q l/min 16.6",
            "Q m3/h 1.5 / Q l/min 25",
        ],
        ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
    ]


def test_normalize_merges_generic_wrapped_rows_with_repeated_anchor() -> None:
    table = TableAsset(
        table_id="table_7",
        document_id="doc_1",
        markdown="tasks",
        table_category="general_table",
        rows=[
            ["Task", "Description"],
            ["1", "Inspect the pump housing and"],
            ["1", "verify the shaft seal."],
        ],
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=1,
                col_end=1,
                text="Inspect the pump housing and verify the shaft seal.",
            )
        ],
    )

    updated = TableRowSemanticNormalizer().normalize(table)

    assert updated is True
    assert table.rows == [
        ["Task", "Description"],
        ["1", "Inspect the pump housing and verify the shaft seal."],
    ]
