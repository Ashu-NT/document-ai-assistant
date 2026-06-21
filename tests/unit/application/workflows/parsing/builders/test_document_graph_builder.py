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
    assert (
        picture.metadata.nearby_text
        == "Refer to the exploded view for part placement."
    )


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

    chunk = find_non_overview_chunks(graph)[0]

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

    overview_chunk = find_chunk_by_type(graph, "overview")
    detail_chunk = find_non_overview_chunks(graph)[0]

    assert len(graph.chunks) == 2
    assert overview_chunk.section_path == ["Procedure"]
    assert "Subsections: Preparation; Execution" in overview_chunk.content
    assert detail_chunk.section_path == ["Procedure"]
    assert "Wear gloves and isolate power." in detail_chunk.content
    assert "Execution" in detail_chunk.content
    assert "Remove the cover and inspect the seal." in detail_chunk.content


def test_document_graph_builder_merges_intro_with_child_task_when_under_budget() -> None:
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

    overview_chunk = find_chunk_by_type(graph, "overview")
    detail_chunk = find_non_overview_chunks(graph)[0]

    assert len(graph.chunks) == 2
    assert overview_chunk.section_path == ["A first DSP project with Code Composer Studio"]
    assert "Subsections: Lab task 1: Feeding the ADC input directly to the DAC output" in overview_chunk.content
    assert detail_chunk.section_path == ["A first DSP project with Code Composer Studio"]
    assert "Lab task 1: Feeding the ADC input directly to the DAC output" in detail_chunk.content


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
    assert "Subsections:" in overview_chunk.content
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

    title_block_chunk = find_chunk_by_path(graph, ["Title block"])
    lamp_labels_chunk = find_chunk_by_path(graph, ["Lamp labels"])
    colreg_chunk = find_chunk_by_path(graph, ["COLREG table"])

    assert "13759/3540-01.00" in title_block_chunk.content
    assert "13 - SIDE LAMP SB - GREEN" in lamp_labels_chunk.content
    assert "Actual 62.23 m" in colreg_chunk.content


def test_document_graph_builder_creates_combined_anchor_and_towing_lamp_chunk() -> None:
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
                text="15 - COMBINED",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=2,
                text="ANCHOR / MASTHEAD LANTERN WHITE / WHITE",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_3",
                element_type=ElementType.TEXT,
                order_index=3,
                text="3540.6000",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_4",
                element_type=ElementType.TEXT,
                order_index=4,
                text="16 - COMBINED",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_5",
                element_type=ElementType.TEXT,
                order_index=5,
                text="ANCHOR/ TOWING LANTERN WHITE / YELLOW",
                page_start=1,
            ),
            make_parsed_element(
                element_id="txt_6",
                element_type=ElementType.TEXT,
                order_index=6,
                text="3540.7000",
                page_start=1,
            ),
        ],
        raw_parsed_document=raw_parsed_document,
    )

    lamp_labels_chunk = find_chunk_by_path(graph, ["Lamp labels"])

    assert "15 - COMBINED" in lamp_labels_chunk.content
    assert "3540.6000" in lamp_labels_chunk.content
    assert "16 - COMBINED" in lamp_labels_chunk.content
    assert "3540.7000" in lamp_labels_chunk.content


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

    approval_chunk = find_chunk_by_path(
        graph,
        [
            "Safety Instructions",
            "Extended order code: Cerabar M",
            "Basic specifications",
        ],
    )

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


def test_document_graph_builder_keeps_unrelated_sibling_sections_separate() -> None:
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
                text="Procedure",
                page_start=1,
                metadata={"heading_level": 1},
            ),
            make_parsed_element(
                element_id="hdr_2",
                element_type=ElementType.SECTION_HEADER,
                order_index=2,
                text="Safety warnings",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_1",
                element_type=ElementType.TEXT,
                order_index=3,
                text="Disconnect the system from power before opening the housing.",
                page_start=1,
            ),
            make_parsed_element(
                element_id="hdr_3",
                element_type=ElementType.SECTION_HEADER,
                order_index=4,
                text="Troubleshooting",
                page_start=1,
                metadata={"heading_level": 2},
            ),
            make_parsed_element(
                element_id="txt_2",
                element_type=ElementType.TEXT,
                order_index=5,
                text="Check the fuse, verify the supply voltage, and inspect the relay.",
                page_start=1,
            ),
        ],
        raw_parsed_document=make_raw_parsed_document(),
    )

    overview_chunk = find_chunk_by_type(graph, "overview")
    detail_chunks = find_non_overview_chunks(graph)

    assert len(graph.chunks) == 3
    assert overview_chunk.section_path == ["Procedure"]
    assert [chunk.section_path for chunk in detail_chunks] == [
        ["Procedure", "Safety warnings"],
        ["Procedure", "Troubleshooting"],
    ]
