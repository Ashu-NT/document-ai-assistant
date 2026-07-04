import pytest

from src.domain.extraction import SemanticSourceMetadata


def _make(**overrides) -> SemanticSourceMetadata:
    defaults = {
        "document_id": "document_001",
        "chunk_id": "chunk_001",
    }
    defaults.update(overrides)
    return SemanticSourceMetadata(**defaults)


def test_requires_document_id() -> None:
    with pytest.raises(ValueError):
        _make(document_id="")


def test_requires_chunk_id() -> None:
    with pytest.raises(ValueError):
        _make(chunk_id="")


def test_rejects_page_start_below_one() -> None:
    with pytest.raises(ValueError):
        _make(page_start=0)


def test_rejects_page_end_below_one() -> None:
    with pytest.raises(ValueError):
        _make(page_end=0)


def test_rejects_page_end_before_page_start() -> None:
    with pytest.raises(ValueError):
        _make(page_start=5, page_end=3)


def test_page_label_with_no_pages() -> None:
    assert _make().page_label == "-"


def test_page_label_with_single_page() -> None:
    assert _make(page_start=4).page_label == "4"


def test_page_label_with_same_start_and_end() -> None:
    assert _make(page_start=4, page_end=4).page_label == "4"


def test_page_label_with_page_range() -> None:
    assert _make(page_start=4, page_end=6).page_label == "4-6"


def test_section_label_with_no_path() -> None:
    assert _make().section_label == "-"


def test_section_label_joins_path_segments() -> None:
    metadata = _make(section_path=("4", "4.2", "Maintenance"))
    assert metadata.section_label == "4 > 4.2 > Maintenance"


def test_to_dict_and_from_dict_round_trip() -> None:
    metadata = SemanticSourceMetadata(
        document_id="document_001",
        chunk_id="chunk_001",
        section_id="section_001",
        section_path=("4", "Maintenance"),
        page_start=4,
        page_end=5,
        parent_section_id="section_root",
        table_id="table_001",
        source_element_ids=("element_001", "element_002"),
        nearby_chunk_ids=("chunk_000", "chunk_002"),
    )

    restored = SemanticSourceMetadata.from_dict(metadata.to_dict())

    assert restored == metadata


def test_from_dict_defaults_missing_optional_fields() -> None:
    restored = SemanticSourceMetadata.from_dict(
        {"document_id": "document_001", "chunk_id": "chunk_001"}
    )

    assert restored.section_id is None
    assert restored.section_path == ()
    assert restored.table_row_id is None
    assert restored.source_element_ids == ()
    assert restored.nearby_chunk_ids == ()
