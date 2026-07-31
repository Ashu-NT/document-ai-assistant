from src.domain.assets import FormAsset, FormField


def test_form_asset_has_fields(sample_form_asset) -> None:
    assert sample_form_asset.has_fields()


def test_form_asset_has_no_fields_when_empty() -> None:
    form_asset = FormAsset(form_id="form_002", document_id="doc_001")

    assert form_asset.has_fields() is False


def test_form_asset_builds_embedding_text(sample_form_asset) -> None:
    embedding_text = sample_form_asset.to_embedding_text()

    assert "Form Caption: Equipment identification form" in embedding_text
    assert "Nearby Text: The following form identifies the equipment." in embedding_text
    assert "Model: HP-001" in embedding_text


def test_form_asset_embedding_text_handles_key_only_field() -> None:
    form_asset = FormAsset(
        form_id="form_003",
        document_id="doc_001",
        fields=[FormField(label="checkbox", key_text="Approved", value_text=None)],
    )

    assert form_asset.to_embedding_text() == "Approved"


def test_form_asset_embedding_text_skips_empty_fields() -> None:
    form_asset = FormAsset(
        form_id="form_004",
        document_id="doc_001",
        fields=[FormField(label=None, key_text=None, value_text=None)],
    )

    assert form_asset.to_embedding_text() == ""
