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

def test_document_graph_builder_creates_spare_parts_table_chunk_for_real_table() -> None:
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
                text="Spare Parts",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="tbl_1",
                element_type=ElementType.TABLE,
                order_index=2,
                text="| Part Number | Description |\n|---|---|\n| HP-001 | Filter |",
                page_start=1,
                metadata={
                    "markdown": "| Part Number | Description |\n|---|---|\n| HP-001 | Filter |",
                    "caption": "Spare parts list",
                    "row_count": 2,
                    "column_count": 2,
                },
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunk = next(iter(graph.chunks.values()))

    assert chunk.chunk_type.value == "spare_parts_table"
    assert "HP-001" in chunk.content

def test_document_graph_builder_merges_short_related_subsections_into_one_chunk() -> None:
    builder = make_builder(max_chunk_tokens=80, chunk_overlap=0)
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
                text="Procedure",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Preparation",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Wear gloves and isolate power.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_3",
                element_type=ElementType.SECTION_HEADER,
                order_index=4,
                text="Execution",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=5,
                text="Remove the cover and inspect the seal.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    # "Preparation" and "Execution" share a parent but neither a title topic
    # nor a recognized content family -- under the section-merge rules,
    # numbering/adjacency alone is never enough, so they stay separate
    # chunks rather than folding into one "detail" chunk.
    overview_chunk = find_chunk_by_type(graph, "overview")
    detail_chunks = find_non_overview_chunks(graph)
    preparation_chunk = next(
        chunk for chunk in detail_chunks if chunk.section_path == ["Procedure", "Preparation"]
    )
    execution_chunk = next(
        chunk for chunk in detail_chunks if chunk.section_path == ["Procedure", "Execution"]
    )

    assert len(graph.chunks) == 3
    assert overview_chunk.section_path == ["Procedure"]
    assert "Direct subsections (2): Preparation; Execution" in overview_chunk.content
    assert "Wear gloves and isolate power." in preparation_chunk.content
    assert "Remove the cover and inspect the seal." in execution_chunk.content

def test_document_graph_builder_keeps_non_introductory_parent_text_separate_from_child_task() -> None:
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
                text="A first DSP project with Code Composer Studio",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text=(
                    "This project introduces the signal path through the ADC and DAC "
                    "and gives the context needed for the first implementation task."
                ),
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=3,
                text="Lab task 1: Feeding the ADC input directly to the DAC output",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.LIST_ITEM,
                order_index=4,
                text="Feed a sine wave into ADC 1 and inspect both output channels.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3",
                element_type=ElementType.LIST_ITEM,
                order_index=5,
                text="Reconnect the cable to ADC 0 and verify the output path again.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    # The parent's title isn't recognized introductory language (e.g.
    # "Overview", "Background"), so its own body text no longer folds into
    # the child task's chunk just because it's short and precedes it --
    # the conservative default keeps them separate.
    chunks = list(graph.chunks.values())
    intro_chunk = next(
        chunk
        for chunk in chunks
        if chunk.section_path == ["A first DSP project with Code Composer Studio"]
    )
    task_chunk = next(
        chunk
        for chunk in chunks
        if chunk.section_path
        == [
            "A first DSP project with Code Composer Studio",
            "Lab task 1: Feeding the ADC input directly to the DAC output",
        ]
    )

    assert len(graph.chunks) == 2
    assert "This project introduces the signal path" in intro_chunk.content
    assert "Feed a sine wave into ADC 1" in task_chunk.content
    assert "Reconnect the cable to ADC 0" in task_chunk.content
