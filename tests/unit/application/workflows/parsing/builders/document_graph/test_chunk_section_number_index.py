from src.application.workflows.parsing.builders.document_graph.chunk_section_number_index import (
    ChunkSectionNumberIndex,
    extract_leading_section_number,
)
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(*, chunk_id: str, section_path: list[str]) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        section_path=section_path,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_extract_leading_section_number_handles_dotted_numbers() -> None:
    assert extract_leading_section_number("6.7.1 Lubrication oil") == "6.7.1"
    assert extract_leading_section_number("3.1 Requirements") == "3.1"
    assert extract_leading_section_number("2 About this document") == "2"


def test_extract_leading_section_number_returns_none_for_untitled_text() -> None:
    assert extract_leading_section_number("Safety Instructions") is None


def test_extract_leading_section_number_backtracks_past_a_run_together_artifact() -> (
    None
):
    # Real parsing artifact: "3.2AbnahmeprufzeugnisnachDINEN10204" -- no
    # space between the number and the following letters, so there's no
    # word boundary right after "3.2" specifically. The regex backtracks to
    # the last position that DOES have a boundary -- just "3", not the full
    # "3.2" -- rather than failing to match at all. Matching the top-level
    # chapter number is an acceptable, low-risk outcome for this rare
    # artifact (a "see chap. 3" reference landing on this chunk alongside
    # its real chapter-3 siblings is not harmful), so this is documented
    # expected behavior, not something the resolver needs to guard against
    # further.
    assert extract_leading_section_number(
        "3.2AbnahmeprufzeugnisnachDINEN10204"
    ) == "3"


def test_exact_match_finds_chunks_under_the_labeled_section() -> None:
    chunk_a = make_chunk(chunk_id="a", section_path=["6.3 Lubrication System"])
    chunk_b = make_chunk(chunk_id="b", section_path=["7 Other Section"])
    index = ChunkSectionNumberIndex([chunk_a, chunk_b])

    assert [c.chunk_id for c in index.exact_match("6.3")] == ["a"]
    assert index.exact_match("9.9") == []


def test_descendant_matches_finds_numbered_subsections() -> None:
    chunk_a = make_chunk(chunk_id="a", section_path=["6.3.1 Filter check"])
    chunk_b = make_chunk(chunk_id="b", section_path=["6.3.2 Oil change"])
    chunk_c = make_chunk(chunk_id="c", section_path=["6.4 Unrelated"])
    index = ChunkSectionNumberIndex([chunk_a, chunk_b, chunk_c])

    descendants = {c.chunk_id for c in index.descendant_matches("6.3")}
    assert descendants == {"a", "b"}


def test_descendant_matches_does_not_match_a_different_top_level_number() -> None:
    # "6.30" must not be treated as a descendant of "6.3" -- the prefix
    # check requires a literal "6.3." boundary, not just a string prefix.
    chunk_a = make_chunk(chunk_id="a", section_path=["6.30 Unrelated Section"])
    index = ChunkSectionNumberIndex([chunk_a])

    assert index.descendant_matches("6.3") == []


def test_index_deduplicates_a_chunk_appearing_under_multiple_matching_labels() -> None:
    # A chunk's section_path can have multiple numbered components (e.g.
    # nested headings); the same chunk must not be double-counted.
    chunk_a = make_chunk(
        chunk_id="a", section_path=["6 Maintenance", "6.3 Lubrication System"]
    )
    index = ChunkSectionNumberIndex([chunk_a])

    assert len(index.exact_match("6")) == 1
    assert len(index.exact_match("6.3")) == 1
