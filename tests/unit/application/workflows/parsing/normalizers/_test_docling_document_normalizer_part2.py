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
        self.export_to_markdown_calls = 0

    def export_to_markdown(self, doc=None) -> str | None:
        self.export_to_markdown_calls += 1
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
        self.iterate_items_calls = 0

    def iterate_items(
        self,
        with_groups: bool = False,
        traverse_pictures: bool = False,
    ):
        del with_groups
        del traverse_pictures
        self.iterate_items_calls += 1
        return [(item, 0) for item in self._items]

def make_raw_parsed_document(raw_document) -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Pump Manual",
        page_count=2,
        raw_document=raw_document,
        parser_name="docling",
    )

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
