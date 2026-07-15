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
        pages: dict[int, object] | None = None,
    ) -> None:
        self._items = items
        self.texts = texts or []
        self.tables = tables or []
        self.pictures = pictures or []
        self.pages = pages or {}
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


def test_normalizer_attaches_layout_metadata_to_canonical_elements() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="text",
                text="Overview text.",
                self_ref="#/texts/1",
                prov=[FakeProvenance(1, FakeBBox(40, 100, 420, 180))],
            ),
            FakeDoclingItem(
                label="text",
                text="Left column detail.",
                self_ref="#/texts/3",
                prov=[FakeProvenance(1, FakeBBox(55, 220, 430, 300))],
            ),
            FakeDoclingItem(
                label="text",
                text="Second column text.",
                self_ref="#/texts/2",
                prov=[FakeProvenance(1, FakeBBox(560, 110, 940, 190))],
            ),
            FakeDoclingItem(
                label="text",
                text="Right column detail.",
                self_ref="#/texts/4",
                prov=[FakeProvenance(1, FakeBBox(575, 230, 950, 310))],
            ),
        ],
        pages={
            1: SimpleNamespace(size=SimpleNamespace(width=1000, height=1400)),
        },
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_002",
    )

    metadata_by_id = {
        element.element_id: element.metadata
        for element in normalized
    }
    left = metadata_by_id["#/texts/1"]
    right = metadata_by_id["#/texts/2"]
    assert left["page_orientation"] == "portrait"
    assert left["layout_lane_count"] == 2
    assert left["layout_lane_index"] == 1
    assert left["layout_region_id"] == "page_1:lane_1"
    assert right["layout_lane_index"] == 2
    assert right["layout_region_id"] == "page_1:lane_2"


def test_normalizer_persists_parallel_table_stream_metadata_for_sparse_side_by_side_tables() -> None:
    raw_document = FakeRawDocument(
        [
            FakeDoclingItem(
                label="table",
                self_ref="#/tables/2",
                markdown="| Left | Right |",
                prov=[FakeProvenance(1)],
                data={
                    "table_cells": [
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                            "text": "Parameter",
                            "prov": [{"page_no": 1, "bbox": {"x1": 40, "y1": 100, "x2": 250, "y2": 120}}],
                        },
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 1,
                            "end_col_offset_idx": 2,
                            "text": "Value",
                            "prov": [{"page_no": 1, "bbox": {"x1": 260, "y1": 100, "x2": 330, "y2": 120}}],
                        },
                        {
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 0,
                            "end_col_offset_idx": 1,
                            "text": "Voltage",
                            "prov": [{"page_no": 1, "bbox": {"x1": 40, "y1": 130, "x2": 250, "y2": 150}}],
                        },
                        {
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 1,
                            "end_col_offset_idx": 2,
                            "text": "400V",
                            "prov": [{"page_no": 1, "bbox": {"x1": 260, "y1": 130, "x2": 330, "y2": 150}}],
                        },
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 2,
                            "end_col_offset_idx": 3,
                            "text": "Parameter",
                            "prov": [{"page_no": 1, "bbox": {"x1": 620, "y1": 100, "x2": 830, "y2": 120}}],
                        },
                        {
                            "start_row_offset_idx": 0,
                            "end_row_offset_idx": 1,
                            "start_col_offset_idx": 3,
                            "end_col_offset_idx": 4,
                            "text": "Value",
                            "prov": [{"page_no": 1, "bbox": {"x1": 840, "y1": 100, "x2": 910, "y2": 120}}],
                        },
                        {
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 2,
                            "end_col_offset_idx": 3,
                            "text": "Frequency",
                            "prov": [{"page_no": 1, "bbox": {"x1": 620, "y1": 130, "x2": 830, "y2": 150}}],
                        },
                        {
                            "start_row_offset_idx": 1,
                            "end_row_offset_idx": 2,
                            "start_col_offset_idx": 3,
                            "end_col_offset_idx": 4,
                            "text": "50Hz",
                            "prov": [{"page_no": 1, "bbox": {"x1": 840, "y1": 130, "x2": 910, "y2": 150}}],
                        },
                    ]
                },
            )
        ],
        pages={
            1: SimpleNamespace(size=SimpleNamespace(width=1000, height=1400)),
        },
    )

    normalized = DoclingDocumentNormalizer().normalize(
        make_raw_parsed_document(raw_document),
        "doc_003",
    )

    metadata = normalized[0].metadata
    assert metadata["table_parallel_stream_count"] == 2
    assert metadata["table_local_reading_order"] == "left_to_right_top_to_bottom"
    assert metadata["table_region_partition_version"] == "1"
    assert metadata["table_structure_tier"] == "parallel_streams"
    assert metadata["table_parallel_stream_rows"] == [
        [["Parameter", "Value"], ["Voltage", "400V"]],
        [["Parameter", "Value"], ["Frequency", "50Hz"]],
    ]
    assert metadata["table_rows"] == [["Parameter", "Value"], ["Voltage", "400V"], ["Frequency", "50Hz"]]
