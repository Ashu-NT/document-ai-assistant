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

def test_document_graph_builder_merges_same_topic_sibling_sections_under_parent() -> None:
    builder = make_builder(max_chunk_tokens=200, chunk_overlap=0)
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
                text="Lab preparation",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="1.2.1 Interrupt handler and bit manipulation",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text=(
                    "Use bit masks to isolate relevant bits before copying the values "
                    "to the DAC output channels."
                ),
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_3",
                element_type=ElementType.SECTION_HEADER,
                order_index=4,
                text="Prep task 1: Interrupt handler and bit manipulation",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.LIST_ITEM,
                order_index=5,
                text="Which decimal values appear at the DAC outputs after masking?",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    overview_chunk = find_chunk_by_type(graph, "overview")
    detail_chunk = find_non_overview_chunks(graph)[0]

    assert len(graph.chunks) == 2
    assert overview_chunk.section_path == ["Lab preparation"]
    assert "Direct subsections (2):" in overview_chunk.content
    assert detail_chunk.section_path == ["Lab preparation"]
    assert "Prep task 1: Interrupt handler and bit manipulation" in detail_chunk.content

def test_document_graph_builder_creates_structured_drawing_chunks() -> None:
    builder = make_builder()
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/nav_lights_arrangement.pdf",
        title="Arrangement Navigation Lights and Signals",
        page_count=1,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/nav_lights_arrangement.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=1,
                text="Title ARRANGEMENT",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=2,
                text="NAVIGATION LIGHTS AND SIGNALS",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Drawing Number",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_4",
                element_type=ElementType.TEXT,
                order_index=4,
                text="13759/3540-01.00",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_5",
                element_type=ElementType.TEXT,
                order_index=5,
                text="Modification",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_6",
                element_type=ElementType.TEXT,
                order_index=6,
                text="18.11.2025 See mod. protocol",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_7",
                element_type=ElementType.TEXT,
                order_index=7,
                text="LENGTH OVER ALL",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_8",
                element_type=ElementType.TEXT,
                order_index=8,
                text="114.20 m",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_9",
                element_type=ElementType.TEXT,
                order_index=9,
                text="Vertical and horizontal positioning and spacing of lights (COLREG)",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_10",
                element_type=ElementType.TEXT,
                order_index=10,
                text="Two masthead lights horizontal distance not less than 0.5 x length overall",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_11",
                element_type=ElementType.TEXT,
                order_index=11,
                text="Desired >57.10 m",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_12",
                element_type=ElementType.TEXT,
                order_index=12,
                text="Actual 62.23 m",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_13",
                element_type=ElementType.TEXT,
                order_index=13,
                text="13 - SIDE LAMP SB - GREEN",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_14",
                element_type=ElementType.TEXT,
                order_index=14,
                text="14 - SIDE LAMP PS - RED",
                page_start=1,
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    title_block_chunk = next(
        chunk for chunk in graph.chunks.values() if "13759/3540-01.00" in chunk.content
    )
    lamp_labels_chunk = next(
        chunk for chunk in graph.chunks.values() if "13 - SIDE LAMP SB - GREEN" in chunk.content
    )
    colreg_chunk = next(
        chunk for chunk in graph.chunks.values() if "Actual 62.23 m" in chunk.content
    )

    assert all(
        chunk.section_path == graph.sections[chunk.section_id].section_path
        for chunk in (title_block_chunk, lamp_labels_chunk, colreg_chunk)
    )
    assert "13759/3540-01.00" in title_block_chunk.content
    assert "13 - SIDE LAMP SB - GREEN" in lamp_labels_chunk.content
    assert "Actual 62.23 m" in colreg_chunk.content
