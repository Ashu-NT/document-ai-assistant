from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.nodes.question_answering.mappers.retrieved_chunk_state_mapper import (
    dict_to_chunk,
    dict_to_citation,
    dict_to_source,
)
from src.domain.common import BoundingBox, ChunkType, SourceLocation
from src.domain.retrieval import Citation, RetrievedChunk, RowBoundingBox


def _make_chunk_with_bboxes() -> RetrievedChunk:
    row_bboxes = [
        RowBoundingBox(
            row_index=2,
            page_number=5,
            bbox=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
        )
    ]
    citation = Citation(
        citation_id="citation_001",
        document_id="doc_001",
        chunk_id="chunk_001",
        source=SourceLocation(
            page_start=5,
            page_end=5,
            bbox=BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0),
        ),
        row_bboxes=row_bboxes,
    )
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content="Replace the filter.",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        source=SourceLocation(
            page_start=5,
            page_end=5,
            bbox=BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0),
        ),
        citation=citation,
    )


def test_source_bbox_round_trips_through_state_dict() -> None:
    chunk = _make_chunk_with_bboxes()

    payload = serialize_graph_value(chunk)
    rebuilt = dict_to_chunk(payload)

    assert rebuilt.source.bbox == BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0)


def test_citation_row_bboxes_round_trip_through_state_dict() -> None:
    chunk = _make_chunk_with_bboxes()

    payload = serialize_graph_value(chunk)
    rebuilt = dict_to_chunk(payload)

    assert rebuilt.citation is not None
    assert rebuilt.citation.row_bboxes == [
        RowBoundingBox(
            row_index=2,
            page_number=5,
            bbox=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
        )
    ]
    assert rebuilt.citation.source.bbox == BoundingBox(x1=10.0, y1=20.0, x2=30.0, y2=40.0)


def test_dict_to_source_returns_none_bbox_when_missing() -> None:
    source = dict_to_source({"page_start": 1, "page_end": 1})

    assert source.bbox is None


def test_dict_to_source_ignores_malformed_bbox() -> None:
    source = dict_to_source({"page_start": 1, "bbox": {"x1": "not-a-number"}})

    assert source.bbox is None


def test_dict_to_citation_ignores_malformed_row_bboxes() -> None:
    citation = dict_to_citation(
        {
            "citation_id": "citation_001",
            "document_id": "doc_001",
            "row_bboxes": [
                {"row_index": 0, "bbox": {"x1": 1.0, "y1": 2.0, "x2": 3.0, "y2": 4.0}},
                {"row_index": "not-an-int", "bbox": {"x1": 1.0, "y1": 2.0, "x2": 3.0, "y2": 4.0}},
                {"row_index": 1, "bbox": {"x1": "bad"}},
                "not-a-dict",
            ],
        }
    )

    assert citation.row_bboxes == [
        RowBoundingBox(
            row_index=0,
            page_number=None,
            bbox=BoundingBox(x1=1.0, y1=2.0, x2=3.0, y2=4.0),
        )
    ]


def test_dict_to_citation_defaults_row_bboxes_to_none_when_absent() -> None:
    citation = dict_to_citation({"citation_id": "citation_001", "document_id": "doc_001"})

    assert citation.row_bboxes is None
