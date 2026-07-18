from src.application.workflows.retrieval.table_focus.retrieved_chunk_table_evidence import (
    has_direct_table_evidence,
    has_spare_parts_table_evidence,
)
from src.domain.common import ChunkType
from src.domain.retrieval import RetrievedChunk


def _chunk(
    *,
    content: str = "Some narrative content.",
    chunk_type: ChunkType = ChunkType.GENERAL,
    metadata: dict[str, str] | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        metadata=metadata or {},
    )


def test_has_direct_table_evidence_true_for_spare_parts_table_chunk_type() -> None:
    chunk = _chunk(chunk_type=ChunkType.SPARE_PARTS_TABLE, content="No markers here")
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_true_for_logical_table_family_id() -> None:
    chunk = _chunk(metadata={"logical_table_family_id": "family_1"})
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_true_for_table_category_metadata() -> None:
    chunk = _chunk(metadata={"table_category": "spare_parts_table"})
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_true_for_table_row_bounds() -> None:
    chunk = _chunk(metadata={"table_row_start": "1"})
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_true_for_hydrated_table_ids_json_list() -> None:
    chunk = _chunk(metadata={"hydrated_table_ids": '["table_1", "table_2"]'})
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_true_for_comma_separated_table_ids() -> None:
    chunk = _chunk(metadata={"table_ids": "table_1, table_2"})
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_false_for_empty_table_ids_list() -> None:
    chunk = _chunk(metadata={"hydrated_table_ids": "[]"})
    assert has_direct_table_evidence(chunk) is False


def test_has_direct_table_evidence_true_for_pipe_delimited_content() -> None:
    chunk = _chunk(content="| Position | Qty |\n| 1 | 2 |")
    assert has_direct_table_evidence(chunk) is True


def test_has_direct_table_evidence_false_for_plain_narrative_content() -> None:
    chunk = _chunk(content="Inspect the filter housing for leaks before restart.")
    assert has_direct_table_evidence(chunk) is False


def test_has_spare_parts_table_evidence_true_for_spare_parts_table_category() -> None:
    chunk = _chunk(
        metadata={"table_category": "spare_parts_table"},
        content="No markers, no digits",
    )
    assert has_spare_parts_table_evidence(chunk) is True


def test_has_spare_parts_table_evidence_true_for_pipe_content_with_marker_and_digit() -> None:
    chunk = _chunk(content="| Pos. | Designation | Qty |\n| 1 | Filter | 2 |")
    assert has_spare_parts_table_evidence(chunk) is True


def test_has_spare_parts_table_evidence_false_without_pipe_or_marker() -> None:
    chunk = _chunk(content="Inspect the filter housing for leaks before restart.")
    assert has_spare_parts_table_evidence(chunk) is False


def test_has_spare_parts_table_evidence_false_when_marker_present_but_no_digit() -> None:
    chunk = _chunk(content="| Designation | Notes |\n| Filter | Clean regularly |")
    assert has_spare_parts_table_evidence(chunk) is False


def test_has_spare_parts_table_evidence_false_for_pipe_content_without_marker_or_digit() -> None:
    chunk = _chunk(content="| Column A | Column B |\n| foo | bar |")
    assert has_spare_parts_table_evidence(chunk) is False
