from src.application.workflows.extraction.batching.extraction_batch import ExtractionBatch
from src.application.workflows.extraction.batching.extraction_oversized_table_batch_expander import (
    expand_oversized_table_batch,
)
from src.application.workflows.extraction.table_windowing import TableEvidenceWindowBuilder
from src.domain.assets import TableAsset
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk

_HEADER = ["Row ID", "Component", "Description"]


def _make_table(row_count: int) -> TableAsset:
    data_rows = [
        [f"ID{n:03d}", f"Component {n}", f"Task {n}"] for n in range(1, row_count + 1)
    ]
    return TableAsset(
        table_id="table_001",
        document_id="doc_001",
        markdown="irrelevant canonical markdown",
        rows=[_HEADER, *data_rows],
    )


def _make_chunk(chunk_id: str, *, table_ids: list[str] | None = None) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content="full canonical rendering",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        table_ids=table_ids or [],
        source=SourceLocation(page_start=1, page_end=1),
    )


def _make_batch(chunks: list[DocumentChunk]) -> ExtractionBatch:
    return ExtractionBatch(
        batch_index=1, batch_count=1, chunks=chunks,
        char_count=sum(len(c.content) for c in chunks), word_count=10,
    )


def test_oversized_table_chunk_expands_into_ordered_windows() -> None:
    chunk = _make_chunk("chunk_001", table_ids=["table_001"])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(
        batch, tables={"table_001": _make_table(39)}, window_builder=builder
    )

    assert result is not None
    assert len(result) == 4
    for window_batch in result:
        assert len(window_batch.chunks) == 1
        assert window_batch.chunks[0].chunk_id == "chunk_001"
    assert [wb.chunks[0].table_row_start for wb in result] == [1, 11, 21, 31]
    assert [wb.chunks[0].table_row_end for wb in result] == [10, 20, 30, 39]


def test_table_header_preserved_in_every_window() -> None:
    chunk = _make_chunk("chunk_001", table_ids=["table_001"])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(
        batch, tables={"table_001": _make_table(39)}, window_builder=builder
    )

    assert result is not None
    for window_batch in result:
        assert "Row ID" in window_batch.chunks[0].content
        assert "Component" in window_batch.chunks[0].content


def test_original_chunk_id_and_page_provenance_preserved_across_windows() -> None:
    chunk = _make_chunk("chunk_canonical", table_ids=["table_001"])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(
        batch, tables={"table_001": _make_table(25)}, window_builder=builder
    )

    assert result is not None
    for window_batch in result:
        view_chunk = window_batch.chunks[0]
        assert view_chunk.chunk_id == "chunk_canonical"
        assert view_chunk.source.page_start == 1
        assert view_chunk.source.page_end == 1


def test_small_table_is_not_expanded() -> None:
    chunk = _make_chunk("chunk_001", table_ids=["table_001"])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(
        batch, tables={"table_001": _make_table(5)}, window_builder=builder
    )

    assert result is None


def test_non_table_chunk_is_not_expanded() -> None:
    chunk = _make_chunk("chunk_001", table_ids=[])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(batch, tables={}, window_builder=builder)

    assert result is None


def test_multi_chunk_batch_is_never_expanded_even_if_a_member_chunk_has_table_ids() -> None:
    chunk_a = _make_chunk("chunk_a", table_ids=["table_001"])
    chunk_b = _make_chunk("chunk_b")
    batch = _make_batch([chunk_a, chunk_b])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(
        batch, tables={"table_001": _make_table(39)}, window_builder=builder
    )

    assert result is None


class _AlwaysWindowButNeverProducesWindowsBuilder:
    """Simulates the defensive edge case: should_window() says this table
    needs windowing, but build_windows() cannot actually produce any -
    the caller must treat this as 'cannot safely window', never fall back
    to sending the raw oversized content unbounded."""

    def should_window(self, table) -> bool:
        return True

    def build_windows(self, table, *, source_chunk_id: str):
        return []


def test_unwindowable_oversized_table_returns_empty_list_not_none() -> None:
    chunk = _make_chunk("chunk_001", table_ids=["table_001"])
    batch = _make_batch([chunk])

    result = expand_oversized_table_batch(
        batch,
        tables={"table_001": _make_table(39)},
        window_builder=_AlwaysWindowButNeverProducesWindowsBuilder(),
    )

    assert result == []


def test_table_ids_referencing_no_known_table_is_not_expanded() -> None:
    chunk = _make_chunk("chunk_001", table_ids=["table_missing"])
    batch = _make_batch([chunk])
    builder = TableEvidenceWindowBuilder(rows_per_window=10)

    result = expand_oversized_table_batch(batch, tables={}, window_builder=builder)

    assert result is None
