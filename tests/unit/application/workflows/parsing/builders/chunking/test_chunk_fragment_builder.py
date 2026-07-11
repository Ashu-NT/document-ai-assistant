from src.application.workflows.parsing.builders.chunking.builders.fragment.chunk_fragment_builder import (
    ChunkFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import (
    BoundingBox,
    ChunkType,
    ElementType,
    ParserMetadata,
    SourceLocation,
)
from src.domain.elements import CanonicalElement


def make_table_element(
    *,
    text: str,
    markdown: str,
    table_rows: list[list[str]] | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id="tbl_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text=text,
        table_id="table_001",
        source=SourceLocation(page_start=1, page_end=1),
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "markdown": markdown,
                **({"table_rows": table_rows} if table_rows is not None else {}),
            },
        ),
    )


def make_picture_element(
    *,
    bbox: BoundingBox | None,
    page_start: int | None = 1,
    caption: str | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id="pic_1",
        document_id="doc_001",
        element_type=ElementType.PICTURE,
        text="Figure 1.",
        picture_id="picture_001",
        source=SourceLocation(page_start=page_start, page_end=page_start, bbox=bbox),
        parser_metadata=(
            ParserMetadata(parser_name="docling", extra={"caption": caption})
            if caption
            else None
        ),
    )


def make_builder(
    *,
    include_picture_chunks: bool,
    page_sizes: dict[int, tuple[float, float]] | None = None,
) -> ChunkFragmentBuilder:
    return ChunkFragmentBuilder(
        text_splitter=ChunkTextSplitter(max_chunk_tokens=200, chunk_overlap=20),
        include_picture_chunks=include_picture_chunks,
        page_sizes=page_sizes,
    )


def test_is_large_picture_false_without_bbox() -> None:
    builder = make_builder(include_picture_chunks=False)
    element = make_picture_element(bbox=None)

    assert builder.picture_fragment_builder.is_large_picture(element) is False


def test_is_large_picture_false_without_page_number() -> None:
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(
        bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800), page_start=None
    )

    assert builder.picture_fragment_builder.is_large_picture(element) is False


def test_is_large_picture_false_when_page_size_unknown() -> None:
    builder = make_builder(include_picture_chunks=False, page_sizes={})
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800))

    assert builder.picture_fragment_builder.is_large_picture(element) is False


def test_is_large_picture_false_for_small_decorative_image() -> None:
    # A small logo in the corner of a 600x800 page: 60x40 = 2400 / 480000 = 0.5%.
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=60, y2=40))

    assert builder.picture_fragment_builder.is_large_picture(element) is False


def test_is_large_picture_true_for_full_page_scan() -> None:
    # A picture covering the whole 600x800 page.
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800))

    assert builder.picture_fragment_builder.is_large_picture(element) is True


def test_is_large_picture_true_at_exact_threshold() -> None:
    # 300 * 800 = 240000, exactly half of 600*800 = 480000.
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(bbox=BoundingBox(x1=0, y1=0, x2=300, y2=800))

    assert builder.picture_fragment_builder.is_large_picture(element) is True


def test_full_page_picture_fragment_kept_despite_include_picture_chunks_false() -> None:
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(
        bbox=BoundingBox(x1=0, y1=0, x2=600, y2=800),
        caption="Scanned certificate page 1",
    )

    fragment = builder._build_fragment_from_element(
        _make_section(), [element], 0, element
    )

    assert fragment is not None
    assert "Scanned certificate page 1" in fragment.text


def test_small_picture_fragment_discarded_when_include_picture_chunks_false() -> None:
    builder = make_builder(
        include_picture_chunks=False,
        page_sizes={1: (600.0, 800.0)},
    )
    element = make_picture_element(
        bbox=BoundingBox(x1=0, y1=0, x2=60, y2=40),
        caption="Company logo",
    )

    fragment = builder._build_fragment_from_element(
        _make_section(), [element], 0, element
    )

    assert fragment is None


def _make_section():
    from src.domain.document import DocumentSection

    return DocumentSection(
        section_id="section_001",
        document_id="doc_001",
        title="Overview",
    )


def test_table_chunk_type_detects_spare_parts_via_header_row_when_text_markers_miss() -> None:
    builder = make_builder(include_picture_chunks=False)
    # No spaces around pipes -- misses the "| part |" text marker -- and no
    # "part number"/"spare part" phrase anywhere in the text either.
    text = "|Part|Description|\n|---|---|\n|HP-001|Filter|"
    element = make_table_element(
        text=text,
        markdown=text,
        table_rows=[["Part", "Description"], ["HP-001", "Filter"]],
    )

    chunk_type = builder.table_fragment_builder.table_chunk_type(element, text)

    assert chunk_type == ChunkType.SPARE_PARTS_TABLE


def test_table_chunk_type_stays_general_without_part_header_or_text_marker() -> None:
    builder = make_builder(include_picture_chunks=False)
    text = "|Position|Description|\n|---|---|\n|1|Filter housing|"
    element = make_table_element(
        text=text,
        markdown=text,
        table_rows=[["Position", "Description"], ["1", "Filter housing"]],
    )

    chunk_type = builder.table_fragment_builder.table_chunk_type(element, text)

    assert chunk_type == ChunkType.GENERAL
