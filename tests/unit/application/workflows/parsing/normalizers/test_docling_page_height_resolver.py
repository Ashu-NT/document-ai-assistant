from types import SimpleNamespace

from src.application.workflows.parsing.normalizers.provenance.docling_page_height_resolver import (
    DoclingPageHeightResolver,
)


def test_resolves_height_from_one_based_docling_page_mapping() -> None:
    raw_document = SimpleNamespace(
        pages={2: SimpleNamespace(size=SimpleNamespace(height=842))}
    )

    assert DoclingPageHeightResolver.resolve(raw_document, 2) == 842.0


def test_resolves_height_from_string_page_mapping_key() -> None:
    raw_document = {"pages": {"3": {"size": {"height": "600"}}}}

    assert DoclingPageHeightResolver.resolve(raw_document, 3) == 600.0


def test_resolves_one_based_page_number_from_sequence() -> None:
    raw_document = {
        "pages": [
            {"size": {"height": 500}},
            {"size": {"height": 700}},
        ]
    }

    assert DoclingPageHeightResolver.resolve(raw_document, 2) == 700.0


def test_returns_none_for_missing_or_invalid_page_height() -> None:
    raw_document = {"pages": {1: {"size": {"height": 0}}}}

    assert DoclingPageHeightResolver.resolve(raw_document, 1) is None
    assert DoclingPageHeightResolver.resolve(raw_document, 2) is None
