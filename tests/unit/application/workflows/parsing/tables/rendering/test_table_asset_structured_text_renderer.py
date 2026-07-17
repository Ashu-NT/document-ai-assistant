from src.application.workflows.parsing.tables.rendering.table_asset_structured_text_renderer import (
    TableAssetStructuredTextRenderer,
)
from src.domain.assets import TableAsset, TableParallelStream


def test_renderer_returns_none_for_empty_rows() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="unused",
    )

    assert TableAssetStructuredTextRenderer().render(table) is None


def test_renderer_renders_labeled_rows() -> None:
    table = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="unused",
        rows=[
            ["Part Number", "Description"],
            ["HP-001", "Filter"],
            ["HP-002", "Gasket"],
        ],
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Row 1: Part Number=HP-001 | Description=Filter\n"
        "Row 2: Part Number=HP-002 | Description=Gasket"
    )


def test_renderer_skips_header_only_table() -> None:
    table = TableAsset(
        table_id="table_003",
        document_id="doc_001",
        markdown="unused",
        rows=[["Part Number", "Description"]],
    )

    assert TableAssetStructuredTextRenderer().render(table) is None


def test_renderer_renders_schedule_matrix() -> None:
    table = TableAsset(
        table_id="table_004",
        document_id="doc_001",
        markdown="unused",
        rows=[
            ["Task", "D", "W", "M"],
            ["Inspect filter", "x", "", "x"],
        ],
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Row 1: Task=Inspect filter | Intervals=Daily, Monthly"
    )


def test_renderer_renders_headerless_key_value_rows() -> None:
    table = TableAsset(
        table_id="table_005",
        document_id="doc_001",
        markdown="unused",
        rows=[
            ["Tank Capacity", "1,200L"],
            ["Pump Capacity", "max 16,000L/hr"],
            ["Voltage", "400V 50Hz"],
        ],
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Row 1: Label=Tank Capacity | Value=1,200L\n"
        "Row 2: Label=Pump Capacity | Value=max 16,000L/hr\n"
        "Row 3: Label=Voltage | Value=400V 50Hz"
    )


def test_renderer_normalizes_spare_parts_tables() -> None:
    table = TableAsset(
        table_id="table_007",
        document_id="doc_001",
        markdown="unused",
        table_category="spare_parts_table",
        rows=[
            [
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
                "SPARE PARTS LIST",
            ],
            [
                "Part Pos. Qty Unit",
                "Designation Size / Dimension, Material / Surface",
                "Part No",
                "",
            ],
            ["0010 1 Pce", "housing", "", ""],
            ["", "0115 1 Pce drive shaft", "", ""],
        ],
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Row 1: Position=0010 | Quantity=1 | Unit=Pce | Description=housing\n"
        "Row 2: Position=0115 | Quantity=1 | Unit=Pce | Description=drive shaft"
    )


def test_renderer_normalizes_troubleshooting_tables() -> None:
    table = TableAsset(
        table_id="table_008",
        document_id="doc_001",
        markdown="unused",
        table_category="troubleshooting_table",
        rows=[
            ["PROBLEM", "PROBABLE CAUSES", "", "POSSIBLE REMEDIES", ""],
            [
                "(1) The motor does not start",
                "1a)",
                "Motor overload protection cuts in",
                "1a)",
                "Check the power supply.",
            ],
        ],
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Row 1: Symptom=(1) The motor does not start | "
        "Cause=Motor overload protection cuts in | "
        "Remedy=Check the power supply."
    )


def test_renderer_renders_parallel_streams_separately() -> None:
    table = TableAsset(
        table_id="table_009",
        document_id="doc_001",
        markdown="unused",
        rows=[["Primary", "Ignored"], ["A", "B"]],
        parallel_stream_rows=[
            [["Part Number", "Description"], ["HP-001", "Filter"]],
            [["Part Number", "Description"], ["HP-002", "Gasket"]],
        ],
        parallel_stream_descriptors=[
            TableParallelStream(
                stream_index=1,
                source_row_start=0,
                source_row_end=1,
                source_col_start=0,
                source_col_end=1,
                row_count=2,
                column_count=2,
                page_number=8,
            ),
            TableParallelStream(
                stream_index=2,
                source_row_start=0,
                source_row_end=1,
                source_col_start=2,
                source_col_end=3,
                row_count=2,
                column_count=2,
                page_number=8,
            ),
        ],
        local_reading_order="left_to_right_top_to_bottom",
    )

    assert TableAssetStructuredTextRenderer().render(table) == (
        "Parallel Table Stream 1 (Left):\n"
        "Row 1: Part Number=HP-001 | Description=Filter\n\n"
        "Parallel Table Stream 2 (Right):\n"
        "Row 1: Part Number=HP-002 | Description=Gasket"
    )
