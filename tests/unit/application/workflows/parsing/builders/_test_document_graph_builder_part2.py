from src.application.workflows.parsing import (
    CanonicalElement as ParsedCanonicalElement,
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

def test_document_graph_builder_creates_picture_reference_chunk_with_context() -> None:
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
                text="Assembly View",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text="Inspect the figure to identify the filter housing.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="pic_1",
                element_type=ElementType.PICTURE,
                order_index=3,
                text="Figure 4. Filter housing layout.",
                page_start=1,
                metadata={
                    "caption": "Figure 4. Filter housing layout.",
                    "ocr_text": "FILTER HOUSING",
                    "image_path": "outputs/images/pic_004.png",
                },
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    picture_chunk = next(
        chunk
        for chunk in graph.chunks.values()
        if chunk.chunk_type.value == "drawing_reference"
    )

    assert "Figure: Figure 4. Filter housing layout." in picture_chunk.content
    assert "Context: Inspect the figure to identify the filter housing." in (
        picture_chunk.content
    )

def test_document_graph_builder_creates_structured_chunk_from_picture_ocr_page() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/inspection_certificate.pdf",
        title="Inspection certificate",
        page_count=1,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/inspection_certificate.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="pic_1",
                element_type=ElementType.PICTURE,
                order_index=1,
                text=None,
                page_start=1,
                metadata={
                    "ocr_text": (
                        "Inspection certificate\n"
                        "Particulars\n"
                        "Quantity 1\n"
                        "Description auxiliary diesel generator\n"
                        "Serial number 536113910"
                    ),
                    "image_path": "outputs/images/pic_001.png",
                },
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    structured_chunk = next(
        (
            chunk
            for chunk in graph.chunks.values()
            if chunk.chunk_type.value == "certification_info"
        ),
        None,
    )

    assert structured_chunk is not None
    assert "auxiliary diesel generator" in structured_chunk.content
    assert "536113910" in structured_chunk.content

def test_document_graph_builder_uses_datasheet_profile_to_skip_picture_chunks() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/adc_converter_datasheet.pdf",
        title="ADC Converter Datasheet",
        page_count=2,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/adc_converter_datasheet.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Electrical Specifications",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=2,
                text="| Parameter | Value |\n|---|---|\n| Supply Voltage | 5V |",
                page_start=1,
                metadata={
                    "markdown": "| Parameter | Value |\n|---|---|\n| Supply Voltage | 5V |",
                    "caption": "Electrical specifications",
                    "row_count": 2,
                    "column_count": 2,
                },
            ),
            make_parsed_element(
                element_id="pic_1",
                element_type=ElementType.PICTURE,
                order_index=3,
                text="Figure 1. Package outline.",
                page_start=1,
                metadata={
                    "caption": "Figure 1. Package outline.",
                    "image_path": "outputs/images/pic_001.png",
                },
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=4,
                text="Mechanical package dimensions are shown in the figure.",
                page_start=1,
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    assert all(
        chunk.chunk_type.value != "drawing_reference"
        for chunk in graph.chunks.values()
    )
