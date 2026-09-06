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

def test_document_graph_builder_creates_approval_matrix_chunk() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pressure_transmitter_report.pdf",
        title="Pressure transmitter report",
        page_count=36,
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
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Safety Instructions",
                page_start=35,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Extended order code: Cerabar M",
                page_start=36,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=3,
                text=(
                    "| Position 1, 2 (Approval) | Description |\n"
                    "|---|---|\n"
                    "| PMC51 PMP5x BG | ATEX II 3 G Ex ic IIC T6...T4 Gc |\n"
                    "| IE | IECEx Ex ic IIC T6...T4 Gc |"
                ),
                page_start=36,
                metadata={
                    "markdown": (
                        "| Position 1, 2 (Approval) | Description |\n"
                        "|---|---|\n"
                        "| PMC51 PMP5x BG | ATEX II 3 G Ex ic IIC T6...T4 Gc |\n"
                        "| IE | IECEx Ex ic IIC T6...T4 Gc |"
                    ),
                    "row_count": 3,
                    "column_count": 2,
                },
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    approval_chunk = next(
        chunk for chunk in graph.chunks.values() if "PMC51 PMP5x BG" in chunk.content
    )

    assert approval_chunk.section_path == graph.sections[
        approval_chunk.section_id
    ].section_path
    assert "PMC51 PMP5x BG" in approval_chunk.content
    assert "ATEX II 3 G Ex ic IIC T6...T4 Gc" in approval_chunk.content
    assert "IECEx Ex ic IIC T6...T4 Gc" in approval_chunk.content

def test_document_graph_builder_creates_structured_sensor_list_chunk() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/fwc12_manual.pdf",
        title="FWC12 Manual",
        page_count=98,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/fwc12_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="7 Components",
                page_start=97,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="7.6 Sensor List",
                page_start=97,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=3,
                text=(
                    "| P&ID Pos Nr. | Service | Function | Type | Part No. |\n"
                    "|---|---|---|---|---|\n"
                    "| M.00.01.01 | Service Tank level | HHL | Fixed point sensor, LMT100 | A00071 |"
                ),
                page_start=97,
                metadata={
                    "markdown": (
                        "| P&ID Pos Nr. | Service | Function | Type | Part No. |\n"
                        "|---|---|---|---|---|\n"
                        "| M.00.01.01 | Service Tank level | HHL | Fixed point sensor, LMT100 | A00071 |"
                    ),
                    "row_count": 2,
                    "column_count": 5,
                },
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    sensor_chunk = find_chunk_by_path(
        graph,
        ["7 Components", "7.6 Sensor List"],
    )

    assert "M.00.01.01" in sensor_chunk.content
    assert "LMT100" in sensor_chunk.content
