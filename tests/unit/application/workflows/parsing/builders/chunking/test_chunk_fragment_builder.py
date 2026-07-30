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
    element_id: str = "tbl_1",
    table_id: str = "table_001",
    text: str,
    markdown: str,
    table_rows: list[list[str]] | None = None,
    metadata: dict | None = None,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text=text,
        table_id=table_id,
        source=SourceLocation(page_start=1, page_end=1),
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "markdown": markdown,
                **({"table_rows": table_rows} if table_rows is not None else {}),
                **(metadata or {}),
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


def make_text_element(
    *,
    element_id: str,
    text: str,
    element_type: ElementType = ElementType.TEXT,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=element_type,
        text=text,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_build_section_fragments_tags_a_contiguous_list_run() -> None:
    builder = make_builder(include_picture_chunks=False)
    section = _make_section()
    elements = [
        make_text_element(element_id="txt_1", text="Do the following:"),
        make_text_element(
            element_id="li_1", text="Step 1.", element_type=ElementType.LIST_ITEM
        ),
        make_text_element(
            element_id="li_2", text="Step 2.", element_type=ElementType.LIST_ITEM
        ),
        make_text_element(
            element_id="li_3", text="Step 3.", element_type=ElementType.LIST_ITEM
        ),
    ]

    fragments = builder.build_section_fragments(
        document_title="Pump Manual",
        document_type=None,
        section=section,
        elements=elements,
    )

    by_element_id = {
        fragment.element_ids[0]: fragment
        for fragment in fragments
        if fragment.element_ids
    }
    assert by_element_id["txt_1"].list_run_id is None
    list_run_id = by_element_id["li_1"].list_run_id
    assert list_run_id is not None
    assert by_element_id["li_2"].list_run_id == list_run_id
    assert by_element_id["li_3"].list_run_id == list_run_id

    expected_total = (
        by_element_id["li_1"].token_count
        + by_element_id["li_2"].token_count
        + by_element_id["li_3"].token_count
    )
    assert by_element_id["li_1"].list_run_total_tokens == expected_total
    assert by_element_id["li_2"].list_run_total_tokens == expected_total
    assert by_element_id["li_3"].list_run_total_tokens == expected_total


def test_build_section_fragments_treats_non_contiguous_lists_as_separate_runs() -> None:
    builder = make_builder(include_picture_chunks=False)
    section = _make_section()
    elements = [
        make_text_element(
            element_id="li_1", text="Step 1.", element_type=ElementType.LIST_ITEM
        ),
        make_text_element(element_id="txt_1", text="An interruption."),
        make_text_element(
            element_id="li_2", text="Step A.", element_type=ElementType.LIST_ITEM
        ),
    ]

    fragments = builder.build_section_fragments(
        document_title="Pump Manual",
        document_type=None,
        section=section,
        elements=elements,
    )

    by_element_id = {
        fragment.element_ids[0]: fragment
        for fragment in fragments
        if fragment.element_ids
    }
    assert by_element_id["li_1"].list_run_id != by_element_id["li_2"].list_run_id


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


def test_build_section_fragments_combines_same_logical_table_family() -> None:
    builder = make_builder(include_picture_chunks=False)
    section = _make_section()
    elements = [
        make_table_element(
            element_id="tbl_1",
            table_id="table_001",
            text="| Task | Monthly |\n|---|---|\n| Inspect filter | x |",
            markdown="| Task | Monthly |\n|---|---|\n| Inspect filter | x |",
            table_rows=[["Task", "Monthly"], ["Inspect filter", "x"]],
            metadata={
                "logical_table_family_id": "table_family_1",
                "family_index": 1,
                "family_total": 2,
                "continuation_role": "start",
                "table_category": "maintenance_interval_table",
                "table_category_confidence": 0.95,
            },
        ),
        make_table_element(
            element_id="tbl_2",
            table_id="table_002",
            text="| Task | Monthly |\n|---|---|\n| Replace gasket | x |",
            markdown="| Task | Monthly |\n|---|---|\n| Replace gasket | x |",
            table_rows=[["Task", "Monthly"], ["Replace gasket", "x"]],
            metadata={
                "logical_table_family_id": "table_family_1",
                "family_index": 2,
                "family_total": 2,
                "continuation_role": "end",
                "table_category": "maintenance_interval_table",
                "table_category_confidence": 0.95,
            },
        ),
    ]

    fragments = builder.build_section_fragments(
        document_title="Pump Manual",
        document_type=None,
        section=section,
        elements=elements,
    )

    family_fragments = [
        fragment
        for fragment in fragments
        if fragment.logical_table_family_id == "table_family_1"
    ]
    assert len(family_fragments) == 1
    fragment = family_fragments[0]
    assert fragment.logical_table_family_id == "table_family_1"
    assert fragment.table_ids == ["table_001", "table_002"]
    assert fragment.table_category == "maintenance_interval_table"
    assert fragment.table_category_confidence == 0.95
    assert fragment.table_row_start == 1
    assert fragment.table_row_end == 2
    assert fragment.table_rows == [
        ["Task", "Monthly"],
        ["Inspect filter", "x"],
        ["Replace gasket", "x"],
    ]


def test_build_section_fragments_merges_structural_fields_across_family_members() -> None:
    builder = make_builder(include_picture_chunks=False)
    section = _make_section()
    elements = [
        make_table_element(
            element_id="tbl_1",
            table_id="table_001",
            text="| Task | Monthly |\n|---|---|\n| Inspect filter | x |",
            markdown="| Task | Monthly |\n|---|---|\n| Inspect filter | x |",
            table_rows=[["Task", "Monthly"], ["Inspect filter", "x"]],
            metadata={
                "logical_table_family_id": "table_family_2",
                "family_index": 1,
                "family_total": 2,
                "continuation_role": "start",
                "table_header_paths_json": [["Task"]],
                "table_axis_summary": {"rows": "task"},
            },
        ),
        make_table_element(
            element_id="tbl_2",
            table_id="table_002",
            text="| Task | Monthly |\n|---|---|\n| Replace gasket | x |",
            markdown="| Task | Monthly |\n|---|---|\n| Replace gasket | x |",
            table_rows=[["Task", "Monthly"], ["Replace gasket", "x"]],
            metadata={
                "logical_table_family_id": "table_family_2",
                "family_index": 2,
                "family_total": 2,
                "continuation_role": "end",
                "table_shape": "record_table",
                "table_structure_quality": 0.8,
                "table_header_paths_json": [["Monthly"]],
                "table_axis_summary": {"columns": "monthly"},
            },
        ),
    ]

    fragments = builder.build_section_fragments(
        document_title="Pump Manual",
        document_type=None,
        section=section,
        elements=elements,
    )

    fragment = next(
        fragment
        for fragment in fragments
        if fragment.logical_table_family_id == "table_family_2"
    )
    assert fragment.table_shape == "record_table"
    assert fragment.table_structure_quality == 0.8
    assert fragment.header_paths == [["Task"], ["Monthly"]]
    assert fragment.axis_summary == {"rows": "task", "columns": "monthly"}
