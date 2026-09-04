from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.chunk_page_index import (
    ChunkPageIndex,
)
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *, chunk_id: str, page_start: int | None, page_end: int | None = None
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        source=SourceLocation(page_start=page_start, page_end=page_end or page_start),
        sequence_number=1,
    )


def test_chunks_for_page_finds_a_single_page_chunk() -> None:
    chunk = make_chunk(chunk_id="c1", page_start=49)
    index = ChunkPageIndex([chunk])

    assert index.chunks_for_page(49) == [chunk]


def test_chunks_for_page_finds_a_multi_page_spanning_chunk_on_every_covered_page() -> (
    None
):
    chunk = make_chunk(chunk_id="c1", page_start=40, page_end=45)
    index = ChunkPageIndex([chunk])

    for page in range(40, 46):
        assert index.chunks_for_page(page) == [chunk]
    assert index.chunks_for_page(39) == []
    assert index.chunks_for_page(46) == []


def test_chunks_for_page_returns_multiple_chunks_when_more_than_one_covers_a_page() -> (
    None
):
    chunk_a = make_chunk(chunk_id="a", page_start=10)
    chunk_b = make_chunk(chunk_id="b", page_start=10)
    index = ChunkPageIndex([chunk_a, chunk_b])

    assert index.chunks_for_page(10) == [chunk_a, chunk_b]


def test_chunks_for_page_skips_chunks_with_no_page_start() -> None:
    chunk = make_chunk(chunk_id="c1", page_start=None)
    index = ChunkPageIndex([chunk])

    assert index.chunks_for_page(1) == []


def test_chunks_for_page_returns_empty_list_for_an_untouched_page() -> None:
    index = ChunkPageIndex([make_chunk(chunk_id="c1", page_start=1)])

    assert index.chunks_for_page(999) == []
