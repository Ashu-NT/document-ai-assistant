from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_number_index import (
    ChunkAnnexNumberIndex,
)
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(*, chunk_id: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content=content,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_matches_a_numeric_annex_label_mentioned_in_chunk_content() -> None:
    chunk = make_chunk(chunk_id="c1", content="8.1 Annex 1\n\nDrawings")
    index = ChunkAnnexNumberIndex([chunk])

    assert [candidate.chunk_id for candidate in index.matches("1")] == ["c1"]


def test_matches_a_letter_appendix_label() -> None:
    chunk = make_chunk(chunk_id="c1", content="Appendix B: Calibration Data")
    index = ChunkAnnexNumberIndex([chunk])

    assert [candidate.chunk_id for candidate in index.matches("B")] == ["c1"]


def test_one_chunk_can_be_indexed_under_multiple_distinct_labels() -> None:
    # Real document shape: a short annex-listing chunk mentioning both
    # "Annex 1" and "Annex 2".
    chunk = make_chunk(
        chunk_id="c1", content="8.1 Annex 1\n\nDrawings\n\n8.2 Annex 2\n\nSensors"
    )
    index = ChunkAnnexNumberIndex([chunk])

    assert [candidate.chunk_id for candidate in index.matches("1")] == ["c1"]
    assert [candidate.chunk_id for candidate in index.matches("2")] == ["c1"]


def test_does_not_index_a_chunk_twice_when_the_same_label_heads_two_lines() -> None:
    chunk = make_chunk(
        chunk_id="c1", content="Annex 2\n\nSensors\n\nAnnex 2 (continued)\n\nMore sensors"
    )
    index = ChunkAnnexNumberIndex([chunk])

    assert [candidate.chunk_id for candidate in index.matches("2")] == ["c1"]


def test_multiple_chunks_can_mention_the_same_annex_label() -> None:
    chunk_a = make_chunk(chunk_id="c1", content="8.2 Annex 2\n\nSensors")
    chunk_b = make_chunk(chunk_id="c2", content="8.2 Annex 2 (continued)\n\nMore sensors")
    index = ChunkAnnexNumberIndex([chunk_a, chunk_b])

    assert {candidate.chunk_id for candidate in index.matches("2")} == {"c1", "c2"}


def test_does_not_index_a_reference_that_only_mentions_the_label_mid_sentence() -> (
    None
):
    # The core fix: a chunk whose own text is a *reference* to an annex
    # ("Refer to Annex 2...") must not be indexed as a candidate TARGET for
    # that same label -- only a heading-style mention at the start of a
    # line counts.
    chunk = make_chunk(chunk_id="c1", content="Refer to Annex 2 for sensor locations.")
    index = ChunkAnnexNumberIndex([chunk])

    assert index.matches("2") == []


def test_returns_empty_list_for_an_unmentioned_label() -> None:
    chunk = make_chunk(chunk_id="c1", content="Nothing annex-related here.")
    index = ChunkAnnexNumberIndex([chunk])

    assert index.matches("9") == []


def test_skips_chunks_with_no_content() -> None:
    chunk = make_chunk(chunk_id="c1", content="")
    index = ChunkAnnexNumberIndex([chunk])

    assert index.matches("1") == []
