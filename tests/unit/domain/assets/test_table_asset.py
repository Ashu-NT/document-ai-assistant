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


def test_table_asset_has_structured_rows_true_when_rows_exist() -> None:
    table = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="unused",
        rows=[["Part Number", "Description"], ["HP-001", "Filter"]],
    )

    assert table.has_structured_rows() is True


def test_table_asset_resolved_table_shape_returns_the_table_shape_field() -> None:
    table = TableAsset(
        table_id="table_014",
        document_id="doc_001",
        markdown="unused",
        table_shape="record_table",
    )

    assert table.resolved_table_shape() == "record_table"


def test_table_asset_resolved_table_shape_is_none_by_default() -> None:
    table = TableAsset(
        table_id="table_015",
        document_id="doc_001",
        markdown="unused",
    )

    assert table.resolved_table_shape() is None


def test_table_asset_to_structured_row_text_echoes_rows_against_header() -> None:
    table = TableAsset(
        table_id="table_012",
        document_id="doc_001",
        markdown="unused",
        rows=[
            ["PROBLEM", "PROBABLE CAUSES", "POSSIBLE REMEDIES"],
            ["(1) The motor does not start", "1a)", "Check the power supply."],
            ["(2) Pump locked", "Prolonged inactivity", "Remove the cause of lockage."],
        ],
    )

    text = table.to_structured_row_text()

    assert text == (
        "Row 1: PROBLEM=(1) The motor does not start | "
        "PROBABLE CAUSES=1a) | POSSIBLE REMEDIES=Check the power supply.\n"
        "Row 2: PROBLEM=(2) Pump locked | "
        "PROBABLE CAUSES=Prolonged inactivity | "
        "POSSIBLE REMEDIES=Remove the cause of lockage."
    )


def test_table_asset_to_structured_row_text_returns_empty_string_without_body_rows() -> None:
    table = TableAsset(
        table_id="table_013",
        document_id="doc_001",
        markdown="unused",
        rows=[["Part Number", "Description"]],
    )

    assert table.to_structured_row_text() == ""
