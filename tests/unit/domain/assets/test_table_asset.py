from src.domain.assets import TableAsset


def test_table_asset_has_content(sample_table_asset) -> None:
    assert sample_table_asset.has_content()


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
