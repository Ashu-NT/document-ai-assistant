def test_table_asset_has_content(sample_table_asset) -> None:
    assert sample_table_asset.has_content()


def test_table_asset_builds_embedding_text(sample_table_asset) -> None:
    embedding_text = sample_table_asset.to_embedding_text()

    assert "Table Caption: Spare parts table" in embedding_text
    assert "HP-001" in embedding_text