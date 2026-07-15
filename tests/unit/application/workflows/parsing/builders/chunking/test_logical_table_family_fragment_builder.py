from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.logical_table_family_fragment_builder import (
    LogicalTableFamilyFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_builder import (
    TableFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


def _make_builder() -> LogicalTableFamilyFragmentBuilder:
    text_splitter = ChunkTextSplitter()
    table_fragment_builder = TableFragmentBuilder(
        text_splitter=text_splitter,
        include_table_context=False,
        asset_context_resolver=AssetContextResolver(
            text_splitter=text_splitter,
            asset_context_window=0,
            asset_context_max_tokens=12,
            element_contributes_to_chunk=lambda _element: True,
        ),
    )
    return LogicalTableFamilyFragmentBuilder(table_fragment_builder=table_fragment_builder)


def _make_section() -> DocumentSection:
    return DocumentSection(section_id="sec_1", document_id="doc_1", title="Specs")


def _make_family_element(
    *,
    element_id: str,
    table_id: str,
    markdown: str,
    rows: list[list[str]],
    page: int,
    family_id: str,
    family_index: int,
    family_total: int,
    continuation_role: str,
    **extra: object,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_1",
        element_type=ElementType.TABLE,
        table_id=table_id,
        source=SourceLocation(page_start=page, page_end=page),
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "markdown": markdown,
                "table_rows": rows,
                "logical_table_family_id": family_id,
                "family_index": family_index,
                "family_total": family_total,
                "continuation_role": continuation_role,
                **extra,
            },
        ),
    )


def test_build_returns_empty_result_when_no_element_belongs_to_a_family() -> None:
    builder = _make_builder()
    element = CanonicalElement(
        element_id="e1",
        document_id="doc_1",
        element_type=ElementType.TABLE,
        table_id="t1",
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={"markdown": "| X |", "table_rows": [["X"]]},
        ),
    )

    result = builder.build(section=_make_section(), elements=[element], excluded_element_ids=set())

    assert result.fragments == []
    assert result.consumed_element_ids == set()


def test_build_excludes_elements_already_consumed_elsewhere() -> None:
    builder = _make_builder()
    element = _make_family_element(
        element_id="e1",
        table_id="t1",
        markdown="| A |",
        rows=[["A"]],
        page=1,
        family_id="fam1",
        family_index=1,
        family_total=1,
        continuation_role="single",
    )

    result = builder.build(
        section=_make_section(),
        elements=[element],
        excluded_element_ids={"e1"},
    )

    assert result.fragments == []
    assert result.consumed_element_ids == set()


def test_build_merges_a_two_member_family_into_a_single_fragment() -> None:
    builder = _make_builder()
    elements = [
        _make_family_element(
            element_id="e1",
            table_id="t1",
            markdown="| A | B |\n|---|---|\n| 1 | 2 |",
            rows=[["A", "B"], ["1", "2"]],
            page=1,
            family_id="fam1",
            family_index=1,
            family_total=2,
            continuation_role="start",
            table_shape="specification_matrix",
            table_structure_quality=0.8,
            table_header_paths_json=[["A"]],
            table_axis_summary={"rows": "a"},
        ),
        _make_family_element(
            element_id="e2",
            table_id="t2",
            markdown="| A | B |\n|---|---|\n| 3 | 4 |",
            rows=[["A", "B"], ["3", "4"]],
            page=2,
            family_id="fam1",
            family_index=2,
            family_total=2,
            continuation_role="end",
            table_shape="record_table",
            table_structure_quality=0.6,
            table_header_paths_json=[["B"]],
            table_axis_summary={"columns": "b"},
        ),
    ]

    result = builder.build(section=_make_section(), elements=elements, excluded_element_ids=set())

    assert len(result.fragments) == 1
    assert result.consumed_element_ids == {"e1", "e2"}
    fragment = result.fragments[0]
    assert fragment.element_ids == ["e1", "e2"]
    assert fragment.table_ids == ["t1", "t2"]
    assert fragment.page_start == 1
    assert fragment.page_end == 2
    assert fragment.table_rows == [["A", "B"], ["1", "2"], ["3", "4"]]
    assert fragment.logical_table_family_id == "fam1"
    assert fragment.logical_table_family_index == 1
    assert fragment.logical_table_family_total == 1
    assert fragment.logical_table_continuation_role == "single"
    # First-non-null shape/quality win from the lead element; header paths and
    # axis summary are unioned across every family member.
    assert fragment.table_shape == "specification_matrix"
    assert fragment.table_structure_quality == 0.8
    assert fragment.header_paths == [["A"], ["B"]]
    assert fragment.axis_summary == {"rows": "a", "columns": "b"}


def test_build_handles_two_independent_families_in_the_same_section() -> None:
    builder = _make_builder()
    elements = [
        _make_family_element(
            element_id="e1",
            table_id="t1",
            markdown="| A |\n|---|\n| 1 |",
            rows=[["A"], ["1"]],
            page=1,
            family_id="fam1",
            family_index=1,
            family_total=1,
            continuation_role="single",
        ),
        _make_family_element(
            element_id="e2",
            table_id="t2",
            markdown="| B |\n|---|\n| 2 |",
            rows=[["B"], ["2"]],
            page=2,
            family_id="fam2",
            family_index=1,
            family_total=1,
            continuation_role="single",
        ),
    ]

    result = builder.build(section=_make_section(), elements=elements, excluded_element_ids=set())

    family_ids = {fragment.logical_table_family_id for fragment in result.fragments}
    assert family_ids == {"fam1", "fam2"}
    assert result.consumed_element_ids == {"e1", "e2"}
