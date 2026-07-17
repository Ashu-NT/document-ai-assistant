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
