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

def test_document_graph_builder_skips_cover_boilerplate_section() -> None:
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
                element_id="hdr_cover",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="DP Lab",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text="April 30, 2026",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Copyright Hochschule Hamburg",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3",
                element_type=ElementType.TEXT,
                order_index=4,
                text="All rights reserved.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3b",
                element_type=ElementType.TEXT,
                order_index=5,
                text=(
                    "Alle Rechte, auch das des auszugsweisen Nachdrucks, der "
                    "auszugsweisen oder vollstandigen Wiedergabe, der Speicherung "
                    "in Datenverarbeitungsanlagen und der Ubersetzung, vorbehalten."
                ),
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=6,
                text="Introduction",
                page_start=2,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_4",
                element_type=ElementType.TEXT,
                order_index=7,
                text="This section contains the real body content for retrieval.",
                page_start=2,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunks = list(graph.chunks.values())

    assert len(chunks) == 1
    assert chunks[0].section_path == ["Introduction"]

def test_document_graph_builder_skips_bibliography_chunks() -> None:
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
                text="Main Topic",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text="Operational guidance.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=3,
                text="Bibliography",
                page_start=2,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=4,
                text="Author: Reference Book, 2024.",
                page_start=2,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunks = list(graph.chunks.values())

    assert len(chunks) == 1
    assert chunks[0].section_path == ["Main Topic"]
    assert "Operational guidance." in chunks[0].content

def test_document_graph_builder_skips_single_column_layout_tables_from_chunks() -> None:
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
                text="Lab task 2",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.LIST_ITEM,
                order_index=2,
                text="Increase the factor scale until you observe an overflow.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=3,
                text="| Lab task 2 |\n|---|\n| Increase the factor scale until you observe an overflow. |",
                page_start=1,
                metadata={
                    "markdown": "| Lab task 2 |\n|---|\n| Increase the factor scale until you observe an overflow. |",
                    "row_count": 1,
                    "column_count": 1,
                },
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunks = list(graph.chunks.values())

    assert len(chunks) == 1
    assert chunks[0].chunk_type.value == "general"
    assert "Increase the factor scale" in chunks[0].content
    assert chunks[0].table_ids == []
