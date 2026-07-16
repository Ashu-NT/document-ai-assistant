from src.domain.common import ElementType, ParserMetadata
from src.domain.document import Document, DocumentGraph, DocumentHashes
from src.domain.elements import CanonicalElement
from src.infrastructure.db.repositories.document.document_graph_asset_rehydrator import (
    rehydrate_assets,
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
                "table_row_ids": ["table_1:row:0", "table_1:row:1"],
                "table_cell_spans": [
                    {
                        "row_start": 0,
                        "row_end": 0,
                        "col_start": 0,
                        "col_end": 0,
                        "text": "Part",
                        "normalized_text": "Part",
                        "raw_lines": ["Part"],
                    }
                ],
                "row_count": 2,
                "column_count": 2,
            },
        )
    )

    rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert table.rows == [["Part", "Description"], ["HP-001", "Filter"]]
    assert table.row_ids == ["table_1:row:0", "table_1:row:1"]
    assert len(table.cell_spans) == 1
    assert table.cell_spans[0].normalized_text == "Part"
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

    rehydrate_assets(graph)

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
                "table_shape": "maintenance_schedule_matrix",
                "table_structure_quality": 0.93,
                "table_header_paths_json": [["Task"], ["Interval", "Daily"]],
                "table_axis_summary": {
                    "row_axis": "task",
                    "column_axis": "interval",
                    "value_axis": "marker",
                },
            },
        )
    )

    rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert table.logical_table_family_id == "table_family_table_1"
    assert table.family_index == 1
    assert table.family_total == 2
    assert table.continuation_role == "start"
    assert table.normalized_header_signature == "task|interval"
    assert table.table_shape == "maintenance_schedule_matrix"
    assert table.table_structure_quality == 0.93
    assert table.header_paths == [["Task"], ["Interval", "Daily"]]
    assert table.axis_summary["row_axis"] == "task"


def test_rehydrate_assets_repairs_table_text_mojibake() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_element(
        _make_table_element(
            table_id="table_1",
            extra={
                "markdown": b"| Description |\n|---|\n| Don\xe2\x80\x99ts \xe2\x86\x92 Setup |".decode(
                    "cp1252"
                ),
                "table_rows": [
                    ["Description"],
                    [b"Don\xe2\x80\x99ts \xe2\x86\x92 Setup".decode("cp1252")],
                ],
            },
        )
    )

    rehydrate_assets(graph)

    table = graph.tables["table_1"]
    assert "Don’ts → Setup" in table.markdown
    assert table.rows == [["Description"], ["Don’ts → Setup"]]


def test_rehydrate_assets_restores_picture_ocr_provenance() -> None:
    graph = DocumentGraph(document=_make_document())
    graph.add_element(
        CanonicalElement(
            element_id="el_pic_1",
            document_id="doc_001",
            element_type=ElementType.PICTURE,
            text="Figure 1",
            picture_id="picture_1",
            parser_metadata=ParserMetadata(
                parser_name="docling",
                extra={
                    "image_path": "outputs/images/picture_1.png",
                    "ocr_text": "MODEL X1",
                    "ocr_provider": "paddleocr",
                    "ocr_confidence": 0.92,
                    "ocr_mode": "asset",
                },
            ),
        )
    )

    rehydrate_assets(graph)

    picture = graph.pictures["picture_1"]
    assert picture.image_path == "outputs/images/picture_1.png"
    assert picture.ocr_text == "MODEL X1"
    assert picture.ocr_provider == "paddleocr"
    assert picture.ocr_confidence == 0.92
    assert picture.ocr_mode == "asset"
