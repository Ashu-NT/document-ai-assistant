from src.domain.assets import TableAsset


def test_table_asset_has_content(sample_table_asset) -> None:
    assert sample_table_asset.has_content()


def test_table_asset_signals_defaults_to_empty_frozenset() -> None:
    table = TableAsset(
        table_id="table_009b",
        document_id="doc_001",
        markdown="unused",
    )

    assert table.signals == frozenset()


def test_table_asset_signals_is_settable() -> None:
    table = TableAsset(
        table_id="table_009c",
        document_id="doc_001",
        markdown="unused",
        signals=frozenset({"identifiers", "specifications"}),
    )

    assert table.signals == frozenset({"identifiers", "specifications"})


def test_table_asset_layout_fields_default_to_none() -> None:
    table = TableAsset(
        table_id="table_010",
        document_id="doc_001",
        markdown="unused",
    )

    assert table.layout_region_id is None
    assert table.layout_region_role is None
    assert table.layout_lane_index is None
    assert table.layout_lane_count is None
    assert table.page_orientation is None


def test_table_asset_layout_fields_are_settable() -> None:
    table = TableAsset(
        table_id="table_011",
        document_id="doc_001",
        markdown="unused",
        layout_region_id="page_3:lane_1",
        layout_region_role="body",
        layout_lane_index=1,
        layout_lane_count=2,
        page_orientation="landscape",
    )

    assert table.layout_region_id == "page_3:lane_1"
    assert table.layout_region_role == "body"
    assert table.layout_lane_index == 1
    assert table.layout_lane_count == 2
    assert table.page_orientation == "landscape"


def test_table_asset_builds_embedding_text(sample_table_asset) -> None:
    embedding_text = sample_table_asset.to_embedding_text()

    assert "Table Caption: Spare parts table" in embedding_text
    assert "HP-001" in embedding_text


def test_table_asset_has_structured_rows_false_when_empty(sample_table_asset) -> None:
    assert sample_table_asset.has_structured_rows() is False
    assert sample_table_asset.to_structured_row_text() is None


def test_table_asset_to_structured_row_text_renders_labeled_rows() -> None:
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

    assert table.has_structured_rows() is True
    text = table.to_structured_row_text()
    assert text == (
        "Row 1: Part Number=HP-001 | Description=Filter\n"
        "Row 2: Part Number=HP-002 | Description=Gasket"
    )


def test_table_asset_to_structured_row_text_returns_none_for_header_only_table() -> None:
    table = TableAsset(
        table_id="table_003",
        document_id="doc_001",
        markdown="unused",
        rows=[["Part Number", "Description"]],
    )

    assert table.to_structured_row_text() is None


def test_table_asset_to_structured_row_text_skips_schedule_marker_headers() -> None:
    table = TableAsset(
        table_id="table_004",
        document_id="doc_001",
        markdown="unused",
        rows=[
            ["Task", "D", "W", "M"],
            ["Inspect filter", "x", "", "x"],
        ],
    )

    assert table.to_structured_row_text() == (
        "Row 1: Task=Inspect filter | Intervals=Daily, Monthly"
    )


def test_table_asset_to_structured_row_text_renders_headerless_key_value_rows() -> None:
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

    assert table.to_structured_row_text() == (
        "Row 1: Label=Tank Capacity | Value=1,200L\n"
        "Row 2: Label=Pump Capacity | Value=max 16,000L/hr\n"
        "Row 3: Label=Voltage | Value=400V 50Hz"
    )


def test_table_asset_to_structured_row_text_normalizes_performance_curve_tables() -> None:
    table = TableAsset(
        table_id="table_006",
        document_id="doc_001",
        markdown="unused",
        rows=[
            [
                "Pump type",
                "Motor power",
                "Motor power",
                "Q m3/h",
                "0",
                "1",
                "1.5",
            ],
            [
                "Pump type",
                "kW",
                "HP",
                "Q l/min",
                "0",
                "16.6",
                "25",
            ],
            ["MXV 25-220C", "3", "4", "H m", "228", "213", "202"],
        ],
    )

    assert table.to_structured_row_text() == (
        "Row 1: Pump type=MXV 25-220C | Motor power (kW)=3 | "
        "Motor power (HP)=4 | Curve metric=H m | "
        "Q m3/h 0 / Q l/min 0=228 | "
        "Q m3/h 1 / Q l/min 16.6=213 | "
        "Q m3/h 1.5 / Q l/min 25=202"
    )


def test_table_asset_to_structured_row_text_normalizes_spare_parts_tables() -> None:
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

    assert table.to_structured_row_text() == (
        "Row 1: Position=0010 | Quantity=1 | Unit=Pce | Description=housing\n"
        "Row 2: Position=0115 | Quantity=1 | Unit=Pce | Description=drive shaft"
    )


def test_table_asset_to_structured_row_text_normalizes_troubleshooting_tables() -> None:
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

    assert table.to_structured_row_text() == (
        "Row 1: Symptom=(1) The motor does not start | "
        "Cause=Motor overload protection cuts in | "
        "Remedy=Check the power supply."
    )


def test_table_asset_to_structured_row_text_renders_parallel_streams_separately() -> None:
    table = TableAsset(
        table_id="table_009",
        document_id="doc_001",
        markdown="unused",
        rows=[["Primary", "Ignored"], ["A", "B"]],
        parallel_stream_rows=[
            [["Part Number", "Description"], ["HP-001", "Filter"]],
            [["Part Number", "Description"], ["HP-002", "Gasket"]],
        ],
        local_reading_order="left_to_right_top_to_bottom",
    )

    assert table.to_structured_row_text() == (
        "Parallel Table Stream 1:\n"
        "Row 1: Part Number=HP-001 | Description=Filter\n\n"
        "Parallel Table Stream 2:\n"
        "Row 1: Part Number=HP-002 | Description=Gasket"
    )
