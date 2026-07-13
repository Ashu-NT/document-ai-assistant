from src.domain.common import ElementType, ParserMetadata
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement
from src.infrastructure.db.repositories.document.document_graph_reader import (
    DocumentGraphReader,
)


def _make_document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="pump_manual.pdf",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(
            file_hash="file_hash_001",
            content_hash="content_hash_001",
        ),
    )


def _make_table_element(*, table_id: str, extra: dict) -> CanonicalElement:
    return CanonicalElement(
        element_id="el_table_1",
        document_id="doc_001",
        element_type=ElementType.TABLE,
        text="| Part | Description |\n|---|---|\n| HP-001 | Filter |",
        table_id=table_id,
        parser_metadata=ParserMetadata(parser_name="docling", extra=extra),
    )


def test_rehydrate_assets_populates_structured_rows_from_parser_extra() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_element(
        _make_table_element(
            table_id="table_1",
            extra={
                "markdown": "| Part | Description |\n|---|---|\n| HP-001 | Filter |",
                "table_rows": [["Part", "Description"], ["HP-001", "Filter"]],
                "row_count": 2,
                "column_count": 2,
            },
        )
    )

    DocumentGraphReader._rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert table.rows == [["Part", "Description"], ["HP-001", "Filter"]]
    assert table.row_count == 2
    assert table.column_count == 2
    assert table.has_structured_rows() is True


def test_rehydrate_assets_defaults_gracefully_when_table_rows_missing() -> None:
    """Documents ingested before this change won't have table_rows in their
    stored parser_extra -- rehydration must not error and must fall back to
    an empty structured representation."""
    graph = DocumentGraph(document=_make_document())
    graph.add_element(
        _make_table_element(
            table_id="table_1",
            extra={
                "markdown": "| Part | Description |\n|---|---|\n| HP-001 | Filter |",
            },
        )
    )

    DocumentGraphReader._rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert table.rows == []
    assert table.row_count is None
    assert table.column_count is None
    assert table.has_structured_rows() is False
    assert table.has_content() is True


def test_rehydrate_assets_restores_logical_table_family_metadata() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_element(
        _make_table_element(
            table_id="table_1",
            extra={
                "markdown": "| Task | Interval |\n|---|---|\n| Inspect filter | Daily |",
                "table_rows": [["Task", "Interval"], ["Inspect filter", "Daily"]],
                "logical_table_family_id": "table_family_table_1",
                "family_index": 1,
                "family_total": 2,
                "continuation_role": "start",
                "normalized_header_signature": "task|interval",
            },
        )
    )

    DocumentGraphReader._rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert table.logical_table_family_id == "table_family_table_1"
    assert table.family_index == 1
    assert table.family_total == 2
    assert table.continuation_role == "start"
    assert table.normalized_header_signature == "task|interval"
