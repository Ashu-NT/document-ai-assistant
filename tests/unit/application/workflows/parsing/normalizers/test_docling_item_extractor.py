from types import SimpleNamespace

from src.application.workflows.parsing.normalizers.docling_item_extractor import (
    DoclingItemExtractor,
)
from src.domain.common import ElementType


class FakeTableExtractor:
    def is_table_item(self, item) -> bool:
        return False


def make_item(label: str):
    return SimpleNamespace(label=label)


def _extractor() -> DoclingItemExtractor:
    return DoclingItemExtractor(FakeTableExtractor())


def test_extract_element_type_maps_footnote_label() -> None:
    result = _extractor().extract_element_type(make_item("footnote"))

    assert result == ElementType.FOOTNOTE


def test_extract_element_type_maps_formula_label() -> None:
    result = _extractor().extract_element_type(make_item("formula"))

    assert result == ElementType.FORMULA


def test_extract_element_type_maps_code_label() -> None:
    result = _extractor().extract_element_type(make_item("code"))

    assert result == ElementType.CODE


def test_extract_element_type_falls_back_to_text_for_unknown_label() -> None:
    result = _extractor().extract_element_type(make_item("something_unrecognized"))

    assert result == ElementType.TEXT
