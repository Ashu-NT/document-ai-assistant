from src.application.workflows.parsing.normalizers.docling_element_text_resolver import (
    DoclingElementTextResolver,
)
from src.application.workflows.parsing.normalizers.table_layout.table_reconstruction_result import (
    TableReconstructionResult,
)
from src.domain.common import ElementType


class _FakeTableExtractor:
    def __init__(self, *, markdown: str | None = None, structure=None) -> None:
        self.markdown = markdown
        self.structure = structure
        self.markdown_calls: list[tuple] = []
        self.structure_calls: list[tuple] = []

    def extract_markdown(self, item, *, doc):
        self.markdown_calls.append((item, doc))
        return self.markdown

    def extract_structure(self, item, *, page_lane_count=None):
        self.structure_calls.append((item, page_lane_count))
        return self.structure


class _FakeCaptionExtractor:
    def __init__(self, *, caption: str | None = None) -> None:
        self.caption = caption

    def extract_caption(self, item):
        return self.caption


class _ExportOnlyItem:
    def __init__(self, markdown: str) -> None:
        self._markdown = markdown

    def export_to_markdown(self) -> str:
        return self._markdown


def test_extract_text_returns_table_markdown_for_table_elements() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        {},
        ElementType.TABLE,
        caption=None,
        table_markdown="| A | B |",
    )

    assert text == "| A | B |"


def test_extract_text_prefers_caption_then_ocr_text_for_pictures() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        {"ocr_text": "scanned text"},
        ElementType.PICTURE,
        caption="Deck filler",
        table_markdown=None,
    )

    assert text == "Deck filler"


def test_extract_text_falls_back_to_ocr_text_when_no_caption() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        {"ocr_text": "scanned text"},
        ElementType.PICTURE,
        caption=None,
        table_markdown=None,
    )

    assert text == "scanned text"


def test_extract_text_uses_first_matching_generic_attribute() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        {"orig": "Maintenance"},
        ElementType.SECTION_HEADER,
        caption=None,
        table_markdown=None,
    )

    assert text == "Maintenance"


def test_extract_text_falls_back_to_export_to_markdown() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        _ExportOnlyItem("Exported content"),
        ElementType.SECTION_HEADER,
        caption=None,
        table_markdown=None,
    )

    assert text == "Exported content"


def test_extract_text_returns_none_when_nothing_matches() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    text = resolver.extract_text(
        {},
        ElementType.SECTION_HEADER,
        caption=None,
        table_markdown=None,
    )

    assert text is None


def test_extract_table_markdown_only_calls_table_extractor_for_tables() -> None:
    table_extractor = _FakeTableExtractor(markdown="| A |")
    resolver = DoclingElementTextResolver(table_extractor)

    assert resolver.extract_table_markdown(
        {}, ElementType.TABLE, raw_document="doc"
    ) == "| A |"
    assert table_extractor.markdown_calls == [({}, "doc")]

    table_extractor.markdown_calls.clear()
    assert (
        resolver.extract_table_markdown({}, ElementType.TEXT, raw_document="doc")
        is None
    )
    assert table_extractor.markdown_calls == []


def test_extract_caption_text_prefers_extractor_then_raw_caption_key() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    assert (
        resolver.extract_caption_text({}, _FakeCaptionExtractor(caption="Figure 1"))
        == "Figure 1"
    )
    assert (
        resolver.extract_caption_text(
            {"caption": "Fallback caption"}, _FakeCaptionExtractor(caption=None)
        )
        == "Fallback caption"
    )


def test_extract_table_structure_only_for_table_elements() -> None:
    structure = TableReconstructionResult(rows=[["A"]])
    resolver = DoclingElementTextResolver(_FakeTableExtractor(structure=structure))

    assert resolver.extract_table_structure({}, ElementType.TABLE) is structure
    assert resolver.extract_table_structure({}, ElementType.TEXT) is None


def test_extract_table_structure_threads_page_lane_count_through() -> None:
    table_extractor = _FakeTableExtractor(
        structure=TableReconstructionResult(rows=[["A"]])
    )
    resolver = DoclingElementTextResolver(table_extractor)

    resolver.extract_table_structure({}, ElementType.TABLE, page_lane_count=2)

    assert table_extractor.structure_calls == [({}, 2)]


def test_extract_section_title_only_for_section_headers() -> None:
    resolver = DoclingElementTextResolver(_FakeTableExtractor())

    assert (
        resolver.extract_section_title(ElementType.SECTION_HEADER, "Maintenance")
        == "Maintenance"
    )
    assert resolver.extract_section_title(ElementType.TEXT, "Maintenance") is None
