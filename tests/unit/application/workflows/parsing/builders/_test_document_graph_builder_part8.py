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

def test_document_graph_builder_creates_structured_report_chunks() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pressure_transmitter_report.pdf",
        title="Pressure transmitter report",
        page_count=1,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pressure_transmitter_report.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=1,
                text="Final Inspection Report",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=2,
                text="Device information",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Description",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_4",
                element_type=ElementType.TEXT,
                order_index=4,
                text="Cerabar M PMP51",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_5",
                element_type=ElementType.TEXT,
                order_index=5,
                text="TAG",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_6",
                element_type=ElementType.TEXT,
                order_index=6,
                text="9180",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_7",
                element_type=ElementType.TEXT,
                order_index=7,
                text="Serial number",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_8",
                element_type=ElementType.TEXT,
                order_index=8,
                text="V8055401129",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_9",
                element_type=ElementType.TEXT,
                order_index=9,
                text="Additional information",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_10",
                element_type=ElementType.TEXT,
                order_index=10,
                text="Output type",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_11",
                element_type=ElementType.TEXT,
                order_index=11,
                text="4...20 mA HART",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_12",
                element_type=ElementType.TEXT,
                order_index=12,
                text="Maximum permissible error",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_13",
                element_type=ElementType.TEXT,
                order_index=13,
                text="±0.1%",
                page_start=1,
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    device_chunk = find_chunk_by_path(
        graph,
        ["Final Inspection Report", "Device information"],
    )
    additional_chunk = find_chunk_by_path(
        graph,
        ["Final Inspection Report", "Additional information"],
    )

    assert "Cerabar M PMP51" in device_chunk.content
    assert "9180" in device_chunk.content
    assert "4...20 mA HART" in additional_chunk.content
    assert "±0.1%" in additional_chunk.content
