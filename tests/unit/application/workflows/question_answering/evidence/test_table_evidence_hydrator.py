import json

from src.application.workflows.question_answering.evidence.table_evidence_hydrator import (
    TableEvidenceHydrator,
)
from src.domain.assets import TableAsset, TableCellSpan
from src.domain.common import BoundingBox, ChunkType, SourceLocation
from src.domain.document import Document, DocumentChunk, DocumentGraph, DocumentHashes
from src.domain.retrieval import Citation, RetrievalQuery, RetrievedChunk


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


def _make_retrieved_chunk(
    *,
    content: str,
    citation: Citation | None = None,
    identifier_values: list[str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        source=SourceLocation(),
        citation=citation,
        identifier_values=identifier_values or [],
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


def test_hydrate_drops_repeated_multi_row_headers_when_family_pages_repeat_them() -> None:
    first = TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="technical data page 1",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Pump", "Calpeda", "SN-001"],
        ],
        logical_table_family_id="table_family_002",
        family_index=1,
        family_total=2,
        table_category="technical_data_table",
        table_shape="record_table",
        header_paths=[["component"], ["manufacturer"], ["serial number"]],
    )
    second = TableAsset(
        table_id="table_002",
        document_id="doc_001",
        markdown="technical data page 2",
        rows=[
            ["Technical data", "Technical data", "Technical data"],
            ["Component", "Manufacturer", "Serial number"],
            ["Motor", "ABB", "SN-002"],
        ],
        logical_table_family_id="table_family_002",
        family_index=2,
        family_total=2,
        table_category="technical_data_table",
        table_shape="record_table",
        header_paths=[["component"], ["manufacturer"], ["serial number"]],
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
            logical_table_family_id="table_family_002",
            table_category="technical_data_table",
        )
    )

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[_make_retrieved_chunk(content=first.markdown)],
        graphs_by_document_id={"doc_001": graph},
    )

    assert json.loads(hydrated[0].metadata["table_rows_json"]) == [
        ["Technical data", "Technical data", "Technical data"],
        ["Component", "Manufacturer", "Serial number"],
        ["Pump", "Calpeda", "SN-001"],
        ["Motor", "ABB", "SN-002"],
    ]
    assert "Row 2: Component=Motor | Manufacturer=ABB | Serial number=SN-002" in hydrated[
        0
    ].content


def _make_citation() -> Citation:
    return Citation(
        citation_id="citation_001",
        document_id="doc_001",
        chunk_id="chunk_001",
    )


def _make_filter_table(*, with_cell_spans: bool) -> TableAsset:
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="| Part | Qty |\n|---|---|\n| HP-001 | 1 |\n| Filter | 2 |",
        rows=[
            ["Part", "Qty"],
            ["HP-001", "1"],
            ["Filter", "2"],
        ],
        cell_spans=(
            [
                TableCellSpan(
                    row_start=2,
                    row_end=2,
                    col_start=0,
                    col_end=0,
                    text="Filter",
                    normalized_text="filter",
                    page_number=3,
                    bbox=BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0),
                ),
                TableCellSpan(
                    row_start=2,
                    row_end=2,
                    col_start=1,
                    col_end=1,
                    text="2",
                    normalized_text="2",
                    page_number=3,
                    bbox=BoundingBox(x1=35.0, y1=20.0, x2=45.0, y2=40.0),
                ),
            ]
            if with_cell_spans
            else []
        ),
    )


def test_hydrate_attaches_row_bboxes_only_for_the_row_matching_the_query() -> None:
    table = _make_filter_table(with_cell_spans=True)
    graph = _make_graph(table=table, source_chunk_content=table.markdown)
    citation = _make_citation()
    chunk = _make_retrieved_chunk(content=table.markdown or "", citation=citation)
    query = RetrievalQuery(query_id="query_001", query_text="Where is the filter located?")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
        query=query,
    )

    assert hydrated[0].citation is not None
    row_bboxes = hydrated[0].citation.row_bboxes
    assert row_bboxes is not None
    assert len(row_bboxes) == 1
    assert row_bboxes[0].row_index == 2
    assert row_bboxes[0].page_number == 3
    assert row_bboxes[0].bbox == BoundingBox(x1=10.0, y1=20.0, x2=45.0, y2=40.0)


def test_hydrate_attaches_no_row_bboxes_when_query_matches_nothing() -> None:
    table = _make_filter_table(with_cell_spans=True)
    graph = _make_graph(table=table, source_chunk_content=table.markdown)
    citation = _make_citation()
    chunk = _make_retrieved_chunk(content=table.markdown or "", citation=citation)
    query = RetrievalQuery(query_id="query_001", query_text="torque specification values")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
        query=query,
    )

    assert hydrated[0].citation is not None
    assert hydrated[0].citation.row_bboxes is None


def test_hydrate_without_query_leaves_citation_row_bboxes_unset() -> None:
    table = _make_filter_table(with_cell_spans=True)
    graph = _make_graph(table=table, source_chunk_content=table.markdown)
    citation = _make_citation()
    chunk = _make_retrieved_chunk(content=table.markdown or "", citation=citation)

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
    )

    assert hydrated[0].citation is not None
    assert hydrated[0].citation.row_bboxes is None


def test_hydrate_skips_row_bboxes_when_no_cell_spans_match_the_selected_row() -> None:
    table = _make_filter_table(with_cell_spans=False)
    graph = _make_graph(table=table, source_chunk_content=table.markdown)
    citation = _make_citation()
    chunk = _make_retrieved_chunk(content=table.markdown or "", citation=citation)
    query = RetrievalQuery(query_id="query_001", query_text="Where is the filter located?")

    hydrated = TableEvidenceHydrator().hydrate(
        chunks=[chunk],
        graphs_by_document_id={"doc_001": graph},
        query=query,
    )

    assert hydrated[0].citation is not None
    assert hydrated[0].citation.row_bboxes is None
