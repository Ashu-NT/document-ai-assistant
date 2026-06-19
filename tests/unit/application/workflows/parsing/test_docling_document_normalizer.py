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
    ) -> None:
        self.label = FakeLabel(label)
        self.text = text
        self.markdown = markdown
        self.caption = caption
        self.image_path = image_path
        self.section_path = section_path
        self.self_ref = self_ref
        self.prov = prov or []

    def export_to_markdown(self) -> str | None:
        return self.markdown


class FakeRawDocument:
    def __init__(self, items: list[FakeDoclingItem]) -> None:
        self._items = items

    def iterate_items(self, with_groups: bool = False, traverse_pictures: bool = False):
        del with_groups
        del traverse_pictures
        return [(item, 0) for item in self._items]


def test_normalize_maps_docling_items_to_canonical_elements() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="section_header",
                text="Maintenance",
                section_path=["Manual", "Maintenance"],
                self_ref="hdr_001",
                prov=[
                    FakeProvenance(
                        1,
                        FakeBBox(1, 2, 3, 4),
                    )
                ],
            ),
            FakeDoclingItem(
                label="text",
                text="Replace the hydraulic filter every 1000 operating hours.",
                section_path=["Manual", "Maintenance"],
                self_ref="txt_001",
                prov=[
                    FakeProvenance(
                        1,
                        FakeBBox(5, 6, 7, 8),
                    )
                ],
            ),
            FakeDoclingItem(
                label="table",
                markdown="| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                caption="Spare parts",
                section_path=["Manual", "Maintenance"],
                self_ref="tbl_001",
                prov=[FakeProvenance(2)],
            ),
            FakeDoclingItem(
                label="picture",
                caption="Exploded hydraulic pump view",
                image_path="outputs/images/pic_001.png",
                section_path=["Manual", "Maintenance"],
                self_ref="pic_001",
                prov=[FakeProvenance(2)],
            ),
        ]
    )
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Pump Manual",
        page_count=2,
        raw_document=raw_document,
        parser_name="docling",
    )

    normalized = DoclingDocumentNormalizer().normalize(
        raw_parsed_document,
        "doc_001",
    )

    assert [element.element_type for element in normalized] == [
        ElementType.SECTION_HEADER,
        ElementType.TEXT,
        ElementType.TABLE,
        ElementType.PICTURE,
    ]
    assert normalized[0].element_id == "hdr_001"
    assert normalized[0].section_title == "Maintenance"
    assert normalized[0].section_path == ["Manual", "Maintenance"]
    assert normalized[1].document_id == "doc_001"
    assert normalized[1].page_start == 1
    assert normalized[1].page_end == 1
    assert normalized[1].bbox is not None
    assert normalized[1].bbox.x1 == 5
    assert normalized[2].text == "| Part | Description |\n|---|---|\n| HP-001 | Filter |"
    assert normalized[2].metadata["markdown"].startswith("| Part |")
    assert normalized[2].metadata["caption"] == "Spare parts"
    assert normalized[3].text == "Exploded hydraulic pump view"
    assert normalized[3].metadata["image_path"] == "outputs/images/pic_001.png"


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
                markdown="| A | B |",
            )
        ],
        pictures=[],
        items=[],
    )
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/fallback.pdf",
        title="Fallback",
        page_count=1,
        raw_document=raw_document,
        parser_name="docling",
    )

    normalized = DoclingDocumentNormalizer().normalize(
        raw_parsed_document,
        "doc_002",
    )

    assert len(normalized) == 2
    assert normalized[0].element_id == "canon_1"
    assert normalized[0].text == "Overview text."
    assert normalized[1].element_type == ElementType.TABLE

