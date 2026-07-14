from src.application.workflows.parsing.tables import LogicalTableFamilyResolver
from src.domain.assets import TableAsset
from src.domain.common import ElementType, ParserMetadata, SourceLocation
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


def _make_table_element(
    *,
    element_id: str,
    table_id: str,
    page_start: int,
    parent_section_id: str = "sec_001",
    reading_order: int = 1,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Header | Value |",
        parent_section_id=parent_section_id,
        reading_order=reading_order,
        source=SourceLocation(page_start=page_start, page_end=page_start),
        table_id=table_id,
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )


def _make_table_asset(
    *,
    table_id: str,
    rows: list[list[str]],
    parent_section_id: str = "sec_001",
    column_count: int | None = None,
) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="| Header | Value |",
        parent_section_id=parent_section_id,
        rows=rows,
        row_count=len(rows),
        column_count=column_count or len(rows[0]),
    )


def test_resolver_groups_adjacent_same_header_tables_into_one_family() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[["Task", "Interval"], ["Inspect filter", "Daily"]],
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[["Task", "Interval"], ["Replace gasket", "Weekly"]],
    )
    graph.add_element(
        _make_table_element(
            element_id="el_1",
            table_id="table_1",
            page_start=10,
            reading_order=1,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_2",
            table_id="table_2",
            page_start=11,
            reading_order=2,
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    first = graph.tables["table_1"]
    second = graph.tables["table_2"]
    assert first.logical_table_family_id == "table_family_table_1"
    assert second.logical_table_family_id == first.logical_table_family_id
    assert first.family_index == 1
    assert first.family_total == 2
    assert first.continuation_role == "start"
    assert second.family_index == 2
    assert second.family_total == 2
    assert second.continuation_role == "end"
    assert first.normalized_header_signature == "task|interval"
    assert (
        graph.elements["el_2"].parser_metadata.extra["logical_table_family_id"]
        == first.logical_table_family_id
    )


def test_resolver_keeps_distinct_table_headers_in_separate_families() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[["Task", "Interval"], ["Inspect filter", "Daily"]],
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[["Part Number", "Description"], ["HP-001", "Filter"]],
    )
    graph.add_element(
        _make_table_element(
            element_id="el_1",
            table_id="table_1",
            page_start=10,
            reading_order=1,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_2",
            table_id="table_2",
            page_start=11,
            reading_order=2,
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    first = graph.tables["table_1"]
    second = graph.tables["table_2"]
    assert first.logical_table_family_id == "table_family_table_1"
    assert second.logical_table_family_id == "table_family_table_2"
    assert first.family_total == 1
    assert second.family_total == 1
    assert first.continuation_role == "single"
    assert second.continuation_role == "single"


def test_resolver_groups_adjacent_document_index_tables_even_without_matching_headers() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[["1", "Introduction", "3"]],
        column_count=3,
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[["2", "Operation", "6"]],
        column_count=3,
    )
    first = _make_table_element(
        element_id="el_1",
        table_id="table_1",
        page_start=2,
        reading_order=1,
    )
    second = _make_table_element(
        element_id="el_2",
        table_id="table_2",
        page_start=3,
        parent_section_id="sec_999",
        reading_order=2,
    )
    first.parser_metadata.extra["item_label"] = "document_index"
    second.parser_metadata.extra["item_label"] = "document_index"
    graph.add_element(first)
    graph.add_element(second)

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_1"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].continuation_role == "end"


def test_resolver_groups_adjacent_document_index_tables_even_with_different_column_counts() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[["1", "Introduction", "3"]],
        column_count=3,
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[["2 Operation 6"]],
        column_count=1,
    )
    first = _make_table_element(
        element_id="el_1",
        table_id="table_1",
        page_start=2,
        reading_order=1,
    )
    second = _make_table_element(
        element_id="el_2",
        table_id="table_2",
        page_start=3,
        parent_section_id="sec_999",
        reading_order=2,
    )
    first.parser_metadata.extra["item_label"] = "document_index"
    second.parser_metadata.extra["item_label"] = "document_index"
    graph.add_element(first)
    graph.add_element(second)

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_1"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].continuation_role == "end"


def test_resolver_groups_adjacent_tables_with_split_header_cells_into_one_family() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[
            [
                "Position No:",
                "Qty: Denomination: Spare Part No: Included in Service Package:",
            ],
            ["P1 1", "Motor"],
        ],
        column_count=5,
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[
            [
                "Position No:",
                "Qty: Denomination: Spare Part",
                "No: Included in Service Package:",
            ],
            ["P2 1", "Carrier", "-18 2"],
        ],
        column_count=5,
    )
    graph.add_element(
        _make_table_element(
            element_id="el_1",
            table_id="table_1",
            page_start=45,
            reading_order=1,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_2",
            table_id="table_2",
            page_start=46,
            reading_order=2,
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_1"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].continuation_role == "end"


def test_resolver_groups_adjacent_tables_when_first_page_has_umbrella_title_row() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = _make_table_asset(
        table_id="table_1",
        rows=[
            ["Technical data", "", ""],
            ["Parameter", "Compact version", "Remote version"],
            ["Pressure range", "0...10", "0...16"],
        ],
        column_count=3,
    )
    graph.tables["table_2"] = _make_table_asset(
        table_id="table_2",
        rows=[
            ["Parameter", "Compact version", "Remote version"],
            ["Flow range", "1...2", "1...3"],
        ],
        column_count=3,
    )
    graph.add_element(
        _make_table_element(
            element_id="el_1",
            table_id="table_1",
            page_start=30,
            reading_order=1,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_2",
            table_id="table_2",
            page_start=31,
            reading_order=2,
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_1"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_1"].normalized_header_signature == (
        "parameter|compact version|remote version"
    )


def test_resolver_does_not_transitively_bridge_unrelated_tables_through_a_headerless_middle_table() -> None:
    """Regression test: a generic, headerless "bridge" table between two
    unrelated umbrella-titled tables can look pairwise-compatible with
    each neighbor individually (each step tolerates only one side having
    a title), but the family as a whole must not merge two genuinely
    unrelated tables like "Bearing Specifications" and "Motor
    Specifications" just because a generic table sat between them.
    """
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_bearing"] = _make_table_asset(
        table_id="table_bearing",
        rows=[
            ["Bearing Specifications", "Bearing Specifications"],
            ["Parameter", "Value"],
            ["Bore", "25mm"],
        ],
        column_count=2,
    )
    graph.tables["table_bridge"] = _make_table_asset(
        table_id="table_bridge",
        rows=[
            ["Parameter", "Value"],
            ["Grease type", "Lithium"],
        ],
        column_count=2,
    )
    graph.tables["table_motor"] = _make_table_asset(
        table_id="table_motor",
        rows=[
            ["Motor Specifications", "Motor Specifications"],
            ["Parameter", "Value"],
            ["Voltage", "400V"],
        ],
        column_count=2,
    )
    graph.add_element(
        _make_table_element(
            element_id="el_bearing",
            table_id="table_bearing",
            page_start=30,
            reading_order=1,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_bridge",
            table_id="table_bridge",
            page_start=31,
            reading_order=2,
        )
    )
    graph.add_element(
        _make_table_element(
            element_id="el_motor",
            table_id="table_motor",
            page_start=32,
            reading_order=3,
        )
    )

    LogicalTableFamilyResolver().resolve(graph)

    assert (
        graph.tables["table_motor"].logical_table_family_id
        != graph.tables["table_bearing"].logical_table_family_id
    )
    assert graph.tables["table_motor"].family_total == 1


def test_resolver_still_groups_a_genuine_four_page_continuation() -> None:
    """The anchor check added for the bridging fix above must not break
    a real multi-page continuation family longer than two tables.
    """
    graph = DocumentGraph(document=_make_document())
    for index, table_id in enumerate(["page_1", "page_2", "page_3", "page_4"]):
        graph.tables[table_id] = _make_table_asset(
            table_id=table_id,
            rows=[
                ["Task", "Interval", "Notes"],
                [f"Task on {table_id}", "Every 6 months", ""],
            ],
            column_count=3,
        )
        graph.add_element(
            _make_table_element(
                element_id=f"el_{table_id}",
                table_id=table_id,
                page_start=40 + index,
                reading_order=index + 1,
            )
        )

    LogicalTableFamilyResolver().resolve(graph)

    family_ids = {
        table_id: graph.tables[table_id].logical_table_family_id
        for table_id in ["page_1", "page_2", "page_3", "page_4"]
    }
    assert len(set(family_ids.values())) == 1
    assert graph.tables["page_4"].family_total == 4
    assert graph.tables["page_4"].continuation_role == "end"
