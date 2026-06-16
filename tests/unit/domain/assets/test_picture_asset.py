def test_picture_asset_has_image_file(sample_picture_asset) -> None:
    assert sample_picture_asset.has_image_file()


def test_picture_asset_has_ocr_text(sample_picture_asset) -> None:
    assert sample_picture_asset.has_ocr_text()


def test_picture_asset_builds_embedding_text(sample_picture_asset) -> None:
    embedding_text = sample_picture_asset.to_embedding_text()

    assert "Figure Caption: Exploded view of hydraulic pump" in embedding_text
    assert "FILTER HOUSING HP-001" in embedding_text