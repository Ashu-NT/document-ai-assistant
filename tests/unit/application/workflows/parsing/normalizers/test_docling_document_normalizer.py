from types import SimpleNamespace

from src.application.workflows.parsing import RawParsedDocument
from src.application.workflows.parsing.normalizers import DoclingDocumentNormalizer
from src.domain.common import ElementType


class FakeLabel:
    def __init__(self, value: str) -> None:
        self.value = value


class FakeBBox:
    def __init__(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class FakeProvenance:
    def __init__(self, page_no: int, bbox: FakeBBox | None = None) -> None:
        self.page_no = page_no
        self.bbox = bbox


class FakeDoclingItem:
    def __init__(
        self,
        *,
        label: str,
        text: str | None = None,
        markdown: str | None = None,
        caption: str | None = None,
        image_path: str | None = None,
        section_path: list[str] | None = None,
        self_ref: str | None = None,
        prov: list[FakeProvenance] | None = None,
        level: int | None = None,
        content_layer: str = "body",
        name: str | None = None,
        parent: dict | None = None,
        captions: list[dict] | None = None,
        data: dict | None = None,
        requires_doc_for_markdown: bool = False,
    ) -> None:
        self.label = FakeLabel(label)
        self.text = text
        self.markdown = markdown
        self.caption = caption
        self.image_path = image_path
        self.section_path = section_path
        self.self_ref = self_ref
        self.prov = prov or []
        self.level = level
        self.content_layer = content_layer
        self.name = name
        self.parent = parent
        self.captions = captions or []
        self.data = data
        self.requires_doc_for_markdown = requires_doc_for_markdown
        self.exported_markdown_doc = None

    def export_to_markdown(self, doc=None) -> str | None:
        if self.requires_doc_for_markdown and doc is None:
            raise AssertionError("doc argument is required for markdown export")
        self.exported_markdown_doc = doc
        return self.markdown


class FakeRawDocument:
    def __init__(
        self,
        items: list[FakeDoclingItem],
        *,
        texts: list[FakeDoclingItem] | None = None,
        tables: list[FakeDoclingItem] | None = None,
        pictures: list[FakeDoclingItem] | None = None,
    ) -> None:
        self._items = items
        self.texts = texts or []
        self.tables = tables or []
        self.pictures = pictures or []

    def iterate_items(
        self,
        with_groups: bool = False,
        traverse_pictures: bool = False,
    ):
        del with_groups
        del traverse_pictures
        return [(item, 0) for item in self._items]


def make_raw_parsed_document(raw_document) -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Pump Manual",
        page_count=2,
        raw_document=raw_document,
        parser_name="docling",
    )


def test_section_header_preserves_heading_level_label_and_raw_ref() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="section_header",
                text="Maintenance",
                self_ref="#/texts/1",
                level=2,
                prov=[FakeProvenance(1, FakeBBox(1, 2, 3, 4))],
            )
        ]
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert normalized[0].element_type == ElementType.SECTION_HEADER
    assert normalized[0].section_title == "Maintenance"
    assert normalized[0].metadata["heading_level"] == 2
    assert normalized[0].metadata["item_label"] == "section_header"
    assert normalized[0].metadata["raw_ref"] == "#/texts/1"


def test_text_element_does_not_use_paragraph_text_as_section_title() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="text",
                text="Replace the hydraulic filter every 1000 operating hours.",
                self_ref="#/texts/2",
                prov=[FakeProvenance(1)],
            )
        ]
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert normalized[0].element_type == ElementType.TEXT
    assert normalized[0].section_title is None
    assert normalized[0].text == "Replace the hydraulic filter every 1000 operating hours."


def test_table_item_becomes_table_element_and_preserves_metadata() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="document_index",
                self_ref="#/tables/0",
                markdown="| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                prov=[FakeProvenance(2)],
                data={
                    "table_cells": [
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                            "text": "Part",
                        },
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 1,
                            "end_col_offset_idx": 2,
                            "text": "Description",
                        },
                    ]
                },
            )
        ]
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert normalized[0].element_type == ElementType.TABLE
    assert normalized[0].text.startswith("| Part |")
    assert normalized[0].metadata["table_rows"] == [["Part", "Description"]]
    assert normalized[0].metadata["row_count"] == 1
    assert normalized[0].metadata["column_count"] == 2


def test_table_item_passes_raw_document_to_markdown_export() -> None:
    table_item = FakeDoclingItem(
        label="table",
        self_ref="#/tables/42",
        prov=[FakeProvenance(2)],
        requires_doc_for_markdown=True,
    )
    raw_document = FakeRawDocument([table_item])

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert normalized[0].element_type == ElementType.TABLE
    assert table_item.exported_markdown_doc is raw_document


def test_picture_item_collects_caption_refs() -> None:
    caption_item = FakeDoclingItem(
        label="caption",
        text="Figure 1. Oscilloscope overview.",
        self_ref="#/texts/10",
    )
    picture_item = FakeDoclingItem(
        label="picture",
        self_ref="#/pictures/2",
        prov=[FakeProvenance(3)],
        image_path="outputs/images/pic_002.png",
        captions=[{"$ref": "#/texts/10"}],
    )
    raw_document = FakeRawDocument(
        [picture_item],
        texts=[caption_item],
        pictures=[picture_item],
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert normalized[0].element_type == ElementType.PICTURE
    assert normalized[0].text == "Figure 1. Oscilloscope overview."
    assert normalized[0].metadata["caption"] == "Figure 1. Oscilloscope overview."
    assert normalized[0].metadata["image_path"] == "outputs/images/pic_002.png"


def test_furniture_page_headers_and_root_body_are_ignored() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="text",
                text="_root_",
                self_ref="#/body",
                name="_root_",
            ),
            FakeDoclingItem(
                label="page_header",
                text="Keysight",
                self_ref="#/texts/99",
                content_layer="furniture",
            ),
            FakeDoclingItem(
                label="page_footer",
                text="Page 1",
                self_ref="#/texts/100",
                content_layer="furniture",
            ),
            FakeDoclingItem(
                label="text",
                text="Real body text.",
                self_ref="#/texts/101",
                prov=[FakeProvenance(1)],
            ),
        ]
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_001",
    )

    assert len(normalized) == 1
    assert normalized[0].element_id == "#/texts/101"
    assert normalized[0].text == "Real body text."


def test_normalize_falls_back_to_raw_document_collections() -> None:
    raw_document = SimpleNamespace(
        texts=[
            FakeDoclingItem(
                label="text",
                text="Overview text.",
            )
        ],
        tables=[
            FakeDoclingItem(
                label="table",
                self_ref="#/tables/1",
                markdown="| A | B |",
            )
        ],
        pictures=[],
        items=[],
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_002",
    )

    assert len(normalized) == 2
    assert normalized[0].element_id == "canon_1"
    assert normalized[0].text == "Overview text."
    assert normalized[1].element_type == ElementType.TABLE
