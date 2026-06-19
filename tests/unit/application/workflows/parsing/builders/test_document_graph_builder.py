from src.application.workflows.parsing import (
    CanonicalElement as ParsedCanonicalElement,
    RawParsedDocument,
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
) -> ParsedCanonicalElement:
    return ParsedCanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        page_start=page_start,
        page_end=page_start,
        bbox=BoundingBox(x1=1, y1=2, x2=3, y2=4),
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


def make_raw_parsed_document() -> RawParsedDocument:
    return RawParsedDocument(
        file_path="data/input/pump_manual.pdf",
        title="Hydraulic Pump Manual",
        page_count=3,
        raw_document=object(),
        parser_name="docling",
        parser_version="1.2.3",
        metadata={"language": "en"},
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

    chunk = next(iter(graph.chunks.values()))

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
    assert picture.metadata.caption == "Figure 1. Exploded view."
    assert picture.image_path == "outputs/images/pic_001.png"


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

    chunk = next(iter(graph.chunks.values()))

    assert "Replace the hydraulic filter" in chunk.content
    assert "MKEYSIGHT" not in chunk.content


def test_document_graph_builder_keeps_whole_elements_when_packing_chunks() -> None:
    builder = make_builder(max_chunk_tokens=12, chunk_overlap=0)
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
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text="alpha beta gamma delta epsilon zeta eta theta",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=3,
                text="iota kappa lambda mu nu xi omicron pi",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    contents = [chunk.content for chunk in graph.chunks.values()]

    assert contents == [
        "alpha beta gamma delta epsilon zeta eta theta",
        "iota kappa lambda mu nu xi omicron pi",
    ]


def test_document_graph_builder_skips_table_of_contents_chunks() -> None:
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
                element_id="hdr_toc",
                element_type=ElementType.SECTION_HEADER,
                order_index=1,
                text="Contents",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="tbl_toc",
                element_type=ElementType.TABLE,
                order_index=2,
                text="| 1 | Introduction | 5 |",
                page_start=1,
                metadata={
                    "markdown": "| 1 | Introduction | 5 |",
                    "item_label": "document_index",
                },
            ),
            make_parsed_element(
                element_id="hdr_1",
                element_type=ElementType.SECTION_HEADER,
                order_index=3,
                text="Introduction",
                page_start=2,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=4,
                text="This section contains the real body content for retrieval.",
                page_start=2,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    chunks = list(graph.chunks.values())

    assert len(chunks) == 1
    assert chunks[0].section_path == ["Introduction"]
    assert "real body content" in chunks[0].content


def test_document_graph_builder_adds_document_and_section_context_to_embedding_text() -> None:
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

    chunk = next(iter(graph.chunks.values()))

    assert chunk.content == "Loading impacts the probe and circuit under test."
    assert "Document title: Hydraulic Pump Manual" in (chunk.embedding_text or "")
    assert (
        "Section path: Oscilloscope Probes > Loading"
        in (chunk.embedding_text or "")
    )


def test_document_graph_builder_splits_large_single_element_by_sentence_boundary() -> None:
    builder = make_builder(max_chunk_tokens=5, chunk_overlap=0)
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
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=2,
                text="Alpha beta gamma. Delta epsilon zeta. Eta theta iota.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    contents = [chunk.content for chunk in graph.chunks.values()]

    assert contents == [
        "Alpha beta gamma.",
        "Delta epsilon zeta.",
        "Eta theta iota.",
    ]


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
