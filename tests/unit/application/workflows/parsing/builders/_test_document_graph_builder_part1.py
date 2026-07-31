from src.application.workflows.parsing import (
    ParsedCanonicalElement,
    RawParsedDocument,
)

from src.application.workflows.parsing.builders.chunking.text.tokenization.chunk_token_counter_factory import (
    ChunkTokenCounterFactory,
)

from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)

from src.domain.common import BoundingBox, ElementType

from src.domain.document import DocumentHashes

from src.shared.ids import IdGenerator

def make_parsed_element(
    *,
    element_id: str,
    element_type: ElementType,
    order_index: int,
    text: str | None,
    page_start: int,
    metadata: dict | None = None,
    bbox: BoundingBox | None = None,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page_start,
        page_end=page_start,
        bbox=bbox or BoundingBox(x1=1, y1=2, x2=3, y2=4),
        order_index=order_index,
        section_title=text if element_type == ElementType.SECTION_HEADER else None,
        raw_ref=element_id,
        metadata=metadata or {},
    )

def make_builder(
    *,
    max_chunk_tokens: int = 200,
    chunk_overlap: int = 20,
) -> DocumentGraphBuilder:
    id_generator = IdGenerator()
    return DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
        max_chunk_tokens=max_chunk_tokens,
        chunk_overlap=chunk_overlap,
    )

def make_raw_parsed_document(
    *,
    raw_document: object | None = None,
    metadata: dict | None = None,
) -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=3,
        raw_document=object() if raw_document is None else raw_document,
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"} if metadata is None else metadata,
    )

class _FakePageSize:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

class _FakePage:
    def __init__(self, width: float, height: float) -> None:
        self.size = _FakePageSize(width, height)

class _FakeRawDocument:
    def __init__(self, pages: dict[int, _FakePage]) -> None:
        self.pages = pages

def find_chunk_by_type(graph, chunk_type: str):
    return next(
        chunk for chunk in graph.chunks.values() if chunk.chunk_type.value == chunk_type
    )

def find_non_overview_chunks(graph):
    return [
        chunk for chunk in graph.chunks.values() if chunk.chunk_type.value != "overview"
    ]

def find_chunk_by_path(graph, path: list[str]):
    return next(
        chunk for chunk in graph.chunks.values() if chunk.section_path == path
    )

def test_document_graph_builder_uses_resolved_section_paths_for_chunks() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Oscilloscope Probes",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Loading",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Loading impacts the probe and circuit under test.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunk = find_non_overview_chunks(graph)[0]

    assert chunk.section_path == ["Oscilloscope Probes", "Loading"]

def test_document_graph_builder_creates_table_assets_and_picture_assets() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Maintenance",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=2,
                text="| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                page_start=1,
                metadata={
                    "markdown": "| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                    "caption": "Spare parts list",
                    "table_rows": [["Part", "Description"], ["HP-001", "Filter"]],
                    "row_count": 2,
                    "column_count": 2,
                },
            ),
            make_parsed_element(
                element_id="pic_1",
                element_type=ElementType.PICTURE,
                order_index=3,
                text="Figure 1. Exploded view.",
                page_start=1,
                metadata={
                    "caption": "Figure 1. Exploded view.",
                    "image_path": "outputs/images/pic_001.png",
                },
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=4,
                text="Refer to the exploded view for part placement.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    table = next(iter(graph.tables.values()))
    picture = next(iter(graph.pictures.values()))

    assert table.metadata.caption == "Spare parts list"
    assert table.rows == [["Part", "Description"], ["HP-001", "Filter"]]
    assert table.row_count == 2
    assert table.column_count == 2
    assert table.has_structured_rows() is True
    assert picture.metadata.caption == "Figure 1. Exploded view."
    assert picture.image_path == "outputs/images/pic_001.png"
    assert (
        picture.metadata.nearby_text
        == "Refer to the exploded view for part placement."
    )

def test_document_graph_builder_creates_form_asset_and_standalone_chunk() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Equipment Identification",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="form_1",
                element_type=ElementType.FORM,
                order_index=2,
                text=None,
                page_start=1,
                metadata={
                    "caption": "Equipment identification form",
                    "form_fields": [
                        {
                            "label": "key",
                            "key_text": "Model",
                            "value_text": "HP-001",
                            "cell_id": 0,
                        }
                    ],
                },
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    form = next(iter(graph.forms.values()))
    assert form.metadata.caption == "Equipment identification form"
    assert form.fields[0].key_text == "Model"
    assert form.fields[0].value_text == "HP-001"

    form_element = next(
        element
        for element in graph.elements.values()
        if element.element_type == ElementType.FORM
    )
    assert form_element.form_id == form.form_id

    form_chunk = find_chunk_by_type(graph, "form_data")
    assert "Model: HP-001" in form_chunk.content


def test_document_graph_builder_does_not_make_chunks_from_picture_ocr_noise() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Maintenance",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_noise",
                element_type=ElementType.TEXT,
                order_index=2,
                text="MKEYSIGHT 500/2500",
                page_start=1,
                metadata={"parent_ref": "#/pictures/2"},
            ),
            make_parsed_element(
                element_id="txt_real",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Replace the hydraulic filter every 1000 operating hours.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunk = find_non_overview_chunks(graph)[0]

    assert "Replace the hydraulic filter" in chunk.content
    assert "MKEYSIGHT" not in chunk.content
