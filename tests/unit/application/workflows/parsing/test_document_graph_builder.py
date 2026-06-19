from src.application.workflows.parsing import (
    CanonicalElement as ParsedCanonicalElement,
    RawParsedDocument,
)
from src.application.workflows.parsing.builders import (
    DocumentGraphBuilder,
    SectionBuilder,
)
from src.domain.common import BoundingBox, ChunkType, ElementType
from src.domain.document import DocumentHashes
from src.shared.ids import IdGenerator


def make_parsed_element(
    *,
    document_id: str,
    element_type: ElementType,
    order_index: int,
    text: str | None,
    page_start: int | None,
    section_path: list[str] | None = None,
    metadata: dict | None = None,
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=f"canon_{order_index}",
        document_id=document_id,
        element_type=element_type,
        text=text,
        page_start=page_start,
        page_end=page_start,
        bbox=BoundingBox(x1=1, y1=2, x2=3, y2=4),
        order_index=order_index,
        section_title=section_path[-1] if section_path else None,
        section_path=section_path or [],
        raw_ref=f"raw_{order_index}",
        metadata=metadata or {},
    )


def test_build_creates_document_graph_with_sections_assets_chunks_and_stats() -> None:
    id_generator = IdGenerator()
    builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
    )
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=2,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
    )
    canonical_elements = [
        make_parsed_element(
            document_id="doc_001",
            element_type=ElementType.SECTION_HEADER,
            order_index=1,
            text="Maintenance",
            page_start=1,
            section_path=["Maintenance"],
        ),
        make_parsed_element(
            document_id="doc_001",
            element_type=ElementType.TEXT,
            order_index=2,
            text="Replace the hydraulic filter every 1000 operating hours.",
            page_start=1,
            section_path=["Maintenance"],
        ),
        make_parsed_element(
            document_id="doc_001",
            element_type=ElementType.TABLE,
            order_index=3,
            text="| Part | Description |\n|---|---|\n| HP-001 | Filter |",
            page_start=2,
            section_path=["Maintenance"],
            metadata={
                "markdown": "| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                "caption": "Spare parts list",
            },
        ),
        make_parsed_element(
            document_id="doc_001",
            element_type=ElementType.PICTURE,
            order_index=4,
            text="Exploded pump assembly",
            page_start=2,
            section_path=["Maintenance"],
            metadata={
                "image_path": "outputs/images/pic_001.png",
                "caption": "Exploded view",
            },
        ),
    ]

    graph = builder.build(
        document_id="doc_001",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
        canonical_elements=canonical_elements,
        raw_parsed_document=raw_parsed_document,
    )

    section = next(iter(graph.sections.values()))
    chunk = next(iter(graph.chunks.values()))
    table = next(iter(graph.tables.values()))
    picture = next(iter(graph.pictures.values()))

    assert graph.document.document_id == "doc_001"
    assert graph.document.title == "Hydraulic Pump Manual"
    assert graph.document.language == "en"
    assert len(graph.sections) == 1
    assert len(graph.elements) == 4
    assert len(graph.chunks) == 1
    assert len(graph.tables) == 1
    assert len(graph.pictures) == 1
    assert section.title == "Maintenance"
    assert len(section.element_ids) == 4
    assert chunk.chunk_type == ChunkType.SPARE_PARTS_TABLE
    assert chunk.section_id == section.section_id
    assert chunk.section_path == ["Maintenance"]
    assert "Replace the hydraulic filter" in chunk.content
    assert chunk.table_ids == [table.table_id]
    assert chunk.picture_ids == [picture.picture_id]
    assert table.table_id.startswith("table_")
    assert picture.picture_id.startswith("picture_")
    assert graph.document.statistics.page_count == 2
    assert graph.document.statistics.element_count == 4
    assert graph.document.statistics.chunk_count == 1


def test_build_creates_default_root_section_when_no_headers_exist() -> None:
    id_generator = IdGenerator()
    builder = DocumentGraphBuilder(
        id_generator=id_generator,
        section_builder=SectionBuilder(id_generator),
    )
    raw_parsed_document = RawParsedDocument(
        file_path="data/input/notes.pdf",
        title=None,
        page_count=1,
        raw_document=object(),
        parser_name="docling",
    )
    canonical_elements = [
        make_parsed_element(
            document_id="doc_002",
            element_type=ElementType.TEXT,
            order_index=1,
            text="General overview content.",
            page_start=1,
        )
    ]

    graph = builder.build(
        document_id="doc_002",
        file_path="data/input/notes.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_002",
            content_hash="content_hash_002",
        ),
        canonical_elements=canonical_elements,
        raw_parsed_document=raw_parsed_document,
    )

    section = next(iter(graph.sections.values()))
    chunk = next(iter(graph.chunks.values()))

    assert len(graph.sections) == 1
    assert section.title == "Document"
    assert section.section_path == ["Document"]
    assert chunk.section_id == section.section_id
    assert chunk.section_path == ["Document"]

