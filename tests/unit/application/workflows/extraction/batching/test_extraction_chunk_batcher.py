from src.application.workflows.extraction.batching import ExtractionChunkBatcher
from src.domain.common import ChunkType, SourceLocation
from src.domain.document import DocumentChunk


def _make_chunk(chunk_id: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id="sec_001",
        content=content,
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance Schedule"],
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_build_batches_char_count_matches_incremental_packing_total() -> None:
    batcher = ExtractionChunkBatcher(max_chunks_per_batch=10, max_chars_per_batch=100_000)
    chunks = [
        _make_chunk("c1", "Replace the hydraulic filter."),
        _make_chunk("c2", "Check the pump housing for leaks."),
        _make_chunk("c3", "Grease the main shaft bearing."),
    ]

    batches = batcher.build_batches(chunks)

    assert len(batches) == 1
    batch = batches[0]
    expected_char_count = sum(
        ExtractionChunkBatcher._estimate_chunk_chars(chunk) for chunk in chunks
    )
    expected_word_count = sum(
        ExtractionChunkBatcher._estimate_chunk_words(chunk) for chunk in chunks
    )
    assert batch.char_count == expected_char_count
    assert batch.word_count == expected_word_count
    assert batch.chunk_ids == ["c1", "c2", "c3"]


def test_build_batches_splits_on_char_limit_and_tracks_char_count_per_batch() -> None:
    batcher = ExtractionChunkBatcher(max_chunks_per_batch=10, max_chars_per_batch=1_000)
    chunks = [_make_chunk(f"c{i}", "word " * 100) for i in range(5)]

    batches = batcher.build_batches(chunks)

    assert len(batches) > 1
    for batch in batches:
        expected_char_count = sum(
            ExtractionChunkBatcher._estimate_chunk_chars(chunk)
            for chunk in batch.chunks
        )
        assert batch.char_count == expected_char_count
        assert batch.batch_count == len(batches)


def test_build_batches_splits_on_chunk_count_limit() -> None:
    batcher = ExtractionChunkBatcher(max_chunks_per_batch=2, max_chars_per_batch=100_000)
    chunks = [_make_chunk(f"c{i}", "short text") for i in range(5)]

    batches = batcher.build_batches(chunks)

    assert [len(batch.chunks) for batch in batches] == [2, 2, 1]


def test_build_single_chunk_batches_preserves_char_and_word_counts() -> None:
    batcher = ExtractionChunkBatcher(max_chunks_per_batch=10, max_chars_per_batch=100_000)
    chunks = [
        _make_chunk("c1", "Replace the hydraulic filter."),
        _make_chunk("c2", "Check the pump housing for leaks."),
    ]
    batch = batcher.build_batches(chunks)[0]

    single_chunk_batches = batcher.build_single_chunk_batches(batch)

    assert len(single_chunk_batches) == 2
    for single_batch, chunk in zip(single_chunk_batches, chunks):
        assert single_batch.char_count == ExtractionChunkBatcher._estimate_chunk_chars(
            chunk
        )
        assert single_batch.word_count == ExtractionChunkBatcher._estimate_chunk_words(
            chunk
        )
