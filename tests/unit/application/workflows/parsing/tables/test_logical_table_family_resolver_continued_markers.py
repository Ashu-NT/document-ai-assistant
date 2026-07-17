from src.application.workflows.parsing.tables import LogicalTableFamilyResolver
from src.domain.assets import TableAsset
from src.domain.common import ElementType, ParserMetadata, SourceLocation
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement


def _document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="manual.pdf",
        file_path="data/input/manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
    )


def _table_element(
    *,
    element_id: str,
    table_id: str,
    page_start: int,
) -> CanonicalElement:
    return CanonicalElement(
        element_id=element_id,
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Header | Value |",
        parent_section_id="sec_001",
        reading_order=page_start,
        source=SourceLocation(page_start=page_start, page_end=page_start),
        table_id=table_id,
        parser_metadata=ParserMetadata(parser_name="docling", extra={}),
    )


def _table_asset(*, table_id: str, rows: list[list[str]]) -> TableAsset:
    return TableAsset(
        table_id=table_id,
        document_id="doc_001",
        markdown="| Header | Value |",
        parent_section_id="sec_001",
        rows=rows,
        row_count=len(rows),
        column_count=len(rows[0]),
    )


def test_resolver_groups_tables_when_later_page_header_is_marked_continued() -> None:
    graph = DocumentGraph(document=_document())
    graph.tables["table_1"] = _table_asset(
        table_id="table_1",
        rows=[["Task", "Interval"], ["Inspect filter", "Daily"]],
    )
    graph.tables["table_2"] = _table_asset(
        table_id="table_2",
        rows=[["Task (continued)", "Interval"], ["Replace gasket", "Weekly"]],
    )
    graph.add_element(_table_element(element_id="el_1", table_id="table_1", page_start=10))
    graph.add_element(_table_element(element_id="el_2", table_id="table_2", page_start=11))

    LogicalTableFamilyResolver().resolve(graph)

    assert graph.tables["table_1"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_2"].logical_table_family_id == "table_family_table_1"
    assert graph.tables["table_1"].normalized_header_signature == "task|interval"
    assert graph.tables["table_2"].normalized_header_signature == "task|interval"
