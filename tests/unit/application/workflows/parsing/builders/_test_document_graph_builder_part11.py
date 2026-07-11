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

def test_document_graph_builder_populates_section_chunk_type_signals() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="h2"),
        canonical_elements=[
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Safety",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Electrical hazards",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="WARNING: Disconnect power before servicing electrical components.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    sections_with_signals = [
        s for s in graph.sections.values() if s.chunk_type_signals
    ]
    assert len(sections_with_signals) > 0
    combined_signals = {
        sig for s in sections_with_signals for sig in s.chunk_type_signals
    }
    assert len(combined_signals) > 0

def test_document_graph_builder_writes_overview_text_to_parent_section() -> None:
    builder = make_builder()
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(file_hash="h1", content_hash="h2"),
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
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Filter replacement",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Replace filter every 500 hours.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_3",
                element_type=ElementType.SECTION_HEADER,
                order_index=4,
                text="Oil change",
                page_start=2,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=5,
                text="Change oil every 1000 hours.",
                page_start=2,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    parent_section = next(
        s for s in graph.sections.values() if s.title == "Maintenance"
    )
    assert parent_section.overview_text is not None
    assert "Maintenance" in parent_section.overview_text
    assert "Filter replacement" in parent_section.overview_text or "Oil change" in parent_section.overview_text

def test_extract_page_sizes_reads_width_and_height_from_raw_document() -> None:
    builder = make_builder()
    raw_document = _FakeRawDocument(
        pages={1: _FakePage(600.0, 800.0), 2: _FakePage(1200.0, 1600.0)}
    )

    page_sizes = builder._extract_page_sizes(
        make_raw_parsed_document(raw_document=raw_document)
    )

    assert page_sizes == {1: (600.0, 800.0), 2: (1200.0, 1600.0)}

def test_extract_page_sizes_returns_empty_dict_when_raw_document_has_no_pages() -> None:
    builder = make_builder()

    page_sizes = builder._extract_page_sizes(make_raw_parsed_document())

    assert page_sizes == {}

def test_document_graph_builder_keeps_full_page_picture_for_certificate_profile() -> None:
    # certificate.yaml sets include_picture_chunks: false — a scanned
    # certificate represented as one full-page PICTURE element must still
    # survive, since the whole document would otherwise produce zero chunks.
    builder = make_builder()
    raw_document = _FakeRawDocument(pages={1: _FakePage(600.0, 800.0)})
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/certificate.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="pic_scan",
                element_type=ElementType.PICTURE,
                order_index=1,
                text="Certificate of Conformity",
                page_start=1,
                bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800),
                metadata={"caption": "Certificate of Conformity"},
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(
            raw_document=raw_document,
            metadata={"document_type": "certificate"},
        ),
    )

    non_overview_chunks = find_non_overview_chunks(graph)
    assert len(non_overview_chunks) == 1
    assert "Certificate of Conformity" in non_overview_chunks[0].content

def test_document_graph_builder_drops_small_decorative_picture_for_certificate_profile() -> None:
    builder = make_builder()
    raw_document = _FakeRawDocument(pages={1: _FakePage(600.0, 800.0)})
    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/certificate.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=[
            make_parsed_element(
                element_id="pic_logo",
                element_type=ElementType.PICTURE,
                order_index=1,
                text="Company Logo",
                page_start=1,
                bbox=BoundingBox(x1=0, y1=0, x2=60, y2=40),
                metadata={"caption": "Company Logo"},
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(
            raw_document=raw_document,
            metadata={"document_type": "certificate"},
        ),
    )

    assert find_non_overview_chunks(graph) == []
