import json

from src.application.workflows.question_answering.evidence.table_evidence_hydrator import (
    TableEvidenceHydrator,
)
from src.domain.assets import TableAsset
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentHashes
from src.domain.retrieval import RetrievedChunk


def _make_document() -> Document:
    return Document(
        document_id="doc_001",
        file_name="pump_manual.pdf",
        file_path="data/input/pump_manual.pdf",
        hashes=DocumentHashes(file_hash="file_hash_001", content_hash="content_hash_001"),
    )


def _make_graph(*, table: TableAsset, source_chunk_content: str) -> DocumentGraph:
    graph = DocumentGraph(document=_make_document())
    graph.tables[table.table_id] = table
    graph.add_chunk(
        DocumentChunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            section_id=None,
            content=source_chunk_content,
            table_ids=[table.table_id],
        )
    )
    return graph


def _make_retrieved_chunk(*, content: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        source=SourceLocation(),
    )


def test_hydrate_stashes_structured_rows_json_when_table_has_rows() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
        rows=[["Part", "Qty"], ["HP-001", "1"]],
    )
    graph = _make_graph(table=table, source_chunk_content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |")
    chunk = _make_retrieved_chunk(content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert len(hydrated) == 1
    assert hydrated[0].metadata["table_evidence_hydrated"] == "true"
    assert json.loads(hydrated[0].metadata["table_rows_json"]) == [
        ["Part", "Qty"],
        ["HP-001", "1"],
    ]
    assert "Row 1: Part=HP-001 | Qty=1" in hydrated[0].content


def test_hydrate_stashes_table_structure_metadata_when_available() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Task | Daily |\n|---|---|\n| Inspect filter | x |",
        rows=[["Task", "Daily"], ["Inspect filter", "x"]],
        table_shape="maintenance_schedule_matrix",
        table_structure_quality=0.92,
        header_paths=[["Task"], ["Interval", "Daily"]],
        axis_summary={"row_axis": "task", "column_axis": "interval"},
    )
    graph = _make_graph(
        table=table,
        source_chunk_content="| Task | Daily |\n|---|---|\n| Inspect filter | x |",
    )
    chunk = _make_retrieved_chunk(content=table.markdown or "")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert hydrated[0].metadata["table_shape"] == "maintenance_schedule_matrix"
    assert hydrated[0].metadata["table_structure_quality"] == "0.92"
    assert json.loads(hydrated[0].metadata["table_header_paths_json"]) == [
        ["Task"],
        ["Interval", "Daily"],
    ]
    assert json.loads(hydrated[0].metadata["table_axis_summary"]) == {
        "row_axis": "task",
        "column_axis": "interval",
    }


def test_hydrate_includes_structure_context_in_hydrated_content() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Task | Daily |\n|---|---|\n| Inspect filter | x |",
        rows=[["Task", "Daily"], ["Inspect filter", "x"]],
        table_shape="maintenance_schedule_matrix",
        header_paths=[["Task"], ["Interval", "Daily"]],
        axis_summary={"row_axis": "task", "column_axis": "interval"},
    )
    graph = _make_graph(
        table=table,
        source_chunk_content="| Task | Daily |\n|---|---|\n| Inspect filter | x |",
    )
    chunk = _make_retrieved_chunk(content=table.markdown or "")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert "Table shape: maintenance_schedule_matrix" in hydrated[0].content
    assert "Header paths: Task | Interval > Daily" in hydrated[0].content
    assert "Axis summary: row_axis=task; column_axis=interval" in hydrated[0].content


def test_hydrate_omits_table_rows_json_when_table_has_no_structured_rows() -> None:
    table = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |",
    )
    graph = _make_graph(table=table, source_chunk_content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |")
    chunk = _make_retrieved_chunk(content="| Part | Qty |\n|---|---|\n| HP-001 | 1 |")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert len(hydrated) == 1
    assert hydrated[0].metadata["table_evidence_hydrated"] == "true"
    assert "table_rows_json" not in hydrated[0].metadata


def test_hydrate_merges_rows_across_logical_table_family() -> None:
    first = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Task | Monthly |\n|---|---|\n| Inspect filter | x |",
        rows=[["Task", "Monthly"], ["Inspect filter", "x"]],
        logical_table_family_id="table_family_001",
        family_index=1,
        family_total=2,
        table_category="maintenance_interval_table",
    )
    second = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="| Task | Monthly |\n|---|---|\n| Replace gasket | x |",
        rows=[["Task", "Monthly"], ["Replace gasket", "x"]],
        logical_table_family_id="table_family_001",
        family_index=2,
        family_total=2,
        table_category="maintenance_interval_table",
    )
    graph = DocumentGraph(document=_make_document())
    graph.tables[first.table_id] = first
    graph.tables[second.table_id] = second
    graph.add_chunk(
        DocumentChunk(
            chunk_id="chunk_001",
            document_id="doc_001",
            section_id=None,
            content=first.markdown,
            table_ids=[first.table_id],
            logical_table_family_id="table_family_001",
            table_category="maintenance_interval_table",
        )
    )
    chunk = _make_retrieved_chunk(content=first.markdown)

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert len(hydrated) == 1
    assert hydrated[0].metadata["logical_table_family_id"] == "table_family_001"
    assert hydrated[0].metadata["table_category"] == "maintenance_interval_table"
    assert json.loads(hydrated[0].metadata["table_rows_json"]) == [
        ["Task", "Monthly"],
        ["Inspect filter", "x"],
        ["Replace gasket", "x"],
    ]
    assert "Replace gasket" in hydrated[0].content
