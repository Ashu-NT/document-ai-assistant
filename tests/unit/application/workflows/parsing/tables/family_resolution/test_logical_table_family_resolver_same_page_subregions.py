from src.application.workflows.parsing.tables import LogicalTableFamilyResolver
from src.domain.assets import TableAsset
from src.domain.common import BoundingBox, ElementType, ParserMetadata, SourceLocation
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement


def _make_document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
    )


def _make_table_asset(
    *,
    table_id: str,
    rows: list[list[str]],
    layout_region_id: str,
    layout_region_role: str = "table_region",
    layout_lane_index: int = 1,
    layout_lane_count: int = 1,
) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="| Header | Value |",
        parent_section_id="sec_001",
        rows=rows,
        row_count=len(rows),
        column_count=len(rows[0]),
        layout_region_id=layout_region_id,
        layout_region_role=layout_region_role,
        layout_lane_index=layout_lane_index,
        layout_lane_count=layout_lane_count,
    )


def _make_table_element(
    *,
    element_id: str,
    table_id: str,
    page_start: int,
    reading_order: int,
    layout_page_order: int,
    bbox: BoundingBox,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Header | Value |",
        parent_section_id="sec_001",
        reading_order=reading_order,
        source=SourceLocation(page_start=page_start, page_end=page_start),
        table_id=table_id,
        parser_metadata=ParserMetadata(
            parser_name="docling",
            extra={
                "layout_page_order": layout_page_order,
                "layout_region_bbox": {
                    "x1": bbox.x1,
                    "y1": bbox.y1,
                    "x2": bbox.x2,
                    "y2": bbox.y2,
                },
            },
        ),
    )


def test_resolver_groups_same_page_sequential_subregions_into_one_family() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_top"] = _make_table_asset(
        table_id="table_top",
        rows=[["Task", "Interval"], ["Inspect filter", "Daily"]],
        layout_region_id="page_12:lane_1:region_1",
    )
    graph.tables["table_bottom"] = _make_table_asset(
        table_id="table_bottom",
        rows=[["Task", "Interval"], ["Replace gasket", "Weekly"]],
        layout_region_id="page_12:lane_1:region_2",
    )
    graph.add_element(
        _make_table_element(
            element_id="el_top",
            table_id="table_top",
            page_start=12,
            reading_order=1,
            layout_page_order=10,
            bbox=BoundingBox(x1=80, y1=120, x2=920, y2=280),
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_bottom",
            table_id="table_bottom",
            page_start=12,
            reading_order=2,
            layout_page_order=11,
            bbox=BoundingBox(x1=90, y1=320, x2=910, y2=470),
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    assert (
        graph.tables["table_bottom"].logical_table_family_id
        == graph.tables["table_top"].logical_table_family_id
    )
    assert graph.tables["table_bottom"].continuation_role == "end"


def test_resolver_does_not_merge_nonsequential_same_lane_subregions() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_top"] = _make_table_asset(
        table_id="table_top",
        rows=[["Task", "Interval"], ["Inspect filter", "Daily"]],
        layout_region_id="page_12:lane_1:region_1",
    )
    graph.tables["table_bottom"] = _make_table_asset(
        table_id="table_bottom",
        rows=[["Task", "Interval"], ["Replace gasket", "Weekly"]],
        layout_region_id="page_12:lane_1:region_3",
    )
    graph.add_element(
        _make_table_element(
            element_id="el_top",
            table_id="table_top",
            page_start=12,
            reading_order=1,
            layout_page_order=10,
            bbox=BoundingBox(x1=80, y1=120, x2=920, y2=280),
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_bottom",
            table_id="table_bottom",
            page_start=12,
            reading_order=2,
            layout_page_order=11,
            bbox=BoundingBox(x1=90, y1=320, x2=910, y2=470),
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_top"].logical_table_family_id == "table_family_table_top"
    assert graph.tables["table_bottom"].logical_table_family_id == "table_family_table_bottom"
