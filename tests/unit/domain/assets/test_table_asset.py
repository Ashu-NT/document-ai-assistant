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

    assert table.to_structured_row_text() is None
