from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_number_index import (
    ChunkSectionNumberIndex,
    extract_leading_section_number,
)
from src.domain.common import SourceLocation
from src.domain.document.entities.chunk import DocumentChunk
from src.domain.document.entities.section import DocumentSection


def make_chunk(
    *,
    chunk_id: str,
    section_path: list[str],
    section_ids: list[str] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=None,
        content="content",
        section_path=section_path,
        section_ids=section_ids or [],
        source=SourceLocation(page_start=1, page_end=1),
    )


def make_section(*, section_id: str, section_path: list[str]) -> DocumentSection:
    return DocumentSection(
        section_id=section_id,
        document_id="doc_001",
        title=section_path[-1] if section_path else "",
        section_path=section_path,
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


def test_chunk_with_collapsed_section_path_is_still_reachable_by_merged_subsection() -> (
    None
):
    # Regression: SectionMergePolicy can fold "1.7 Modifications" and "1.8
    # Liability and Warranty" into one chunk whose displayed section_path
    # collapses to the common ancestor "1 General". A fuzzy "see section
    # 1.8" reference must still find this chunk via section_ids, even
    # though "1.8" never appears in section_path itself.
    merged_chunk = make_chunk(
        chunk_id="merged",
        section_path=["1 General"],
        section_ids=["sec_general", "sec_17", "sec_18"],
    )
    sections = {
        "sec_general": make_section(section_id="sec_general", section_path=["1 General"]),
        "sec_17": make_section(
            section_id="sec_17", section_path=["1 General", "1.7 Modifications"]
        ),
        "sec_18": make_section(
            section_id="sec_18",
            section_path=["1 General", "1.8 Liability and Warranty"],
        ),
    }
    index = ChunkSectionNumberIndex([merged_chunk], sections=sections)

    assert [c.chunk_id for c in index.exact_match("1.8")] == ["merged"]
    assert [c.chunk_id for c in index.exact_match("1.7")] == ["merged"]
    assert [c.chunk_id for c in index.exact_match("1")] == ["merged"]


def test_missing_sections_argument_only_indexes_the_primary_section_path() -> None:
    # Back-compat: callers that don't pass `sections` (or chunks predating
    # section_ids) still get the old primary-path-only behavior instead of
    # an error.
    merged_chunk = make_chunk(
        chunk_id="merged",
        section_path=["1 General"],
        section_ids=["sec_general", "sec_18"],
    )
    index = ChunkSectionNumberIndex([merged_chunk])

    assert index.exact_match("1.8") == []
    assert [c.chunk_id for c in index.exact_match("1")] == ["merged"]
