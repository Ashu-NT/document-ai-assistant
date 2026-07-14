from src.application.workflows.parsing.tables import TableSemanticResolver
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


def test_table_semantic_resolver_persists_maintenance_structure_metadata() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.tables["table_1"] = TableAsset(
        table_id="table_1",
        document_id="doc_001",
        markdown="| Task | D | W | M |",
        rows=[
            ["Task", "D", "W", "M"],
            ["Inspect basket", "x", "", "x"],
        ],
        row_count=2,
        column_count=4,
    )
    graph.add_element(
        CanonicalElement(
            element_id="el_table_1",
            document_id="doc_001",
            element_type=ElementType.TABLE,
            text="| Task | D | W | M |",
            table_id="table_1",
            source=SourceLocation(page_start=12, page_end=12),
            parser_metadata=ParserMetadata(parser_name="docling", extra={}),
        )
    )

    TableSemanticResolver().resolve(graph)

    table = graph.tables["table_1"]
    parser_extra = graph.elements["el_table_1"].parser_metadata.extra

    assert table.table_category == "maintenance_interval_table"
    assert table.table_shape == "maintenance_schedule_matrix"
    assert table.table_structure_quality is not None
    assert table.header_paths == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
    ]
    assert table.axis_summary["column_axis"] == "interval"
    assert parser_extra["table_shape"] == "maintenance_schedule_matrix"
    assert parser_extra["table_header_paths_json"] == [
        ["Task"],
        ["Interval", "Daily"],
        ["Interval", "Weekly"],
        ["Interval", "Monthly"],
    ]
    assert parser_extra["table_axis_summary"]["value_axis"] == "marker"
