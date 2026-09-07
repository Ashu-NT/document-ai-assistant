from src.application.workflows.retrieval.context_expansion.document_chunk_index import (
    DocumentChunkIndex,
)
from src.domain.common import ChunkType, SourceLocation
from src.domain.document.entities.chunk import DocumentChunk


def make_chunk(
    *,
    chunk_id: str,
    section_id: str | None,
    section_path: list[str],
    section_ids: list[str] | None = None,
    sequence_number: int = 1,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        section_id=section_id,
        content="content",
        section_path=section_path,
        section_ids=section_ids or [],
        sequence_number=sequence_number,
        source=SourceLocation(page_start=1, page_end=1),
    )


def test_by_section_id_index_also_covers_a_merged_chunks_touched_sections() -> None:
    # Regression: a chunk merged from sibling subsections (see
    # SectionMergePolicy / ChunkPayloadFactory) displays a collapsed primary
    # section_id but must still be found by any of its touched sections.
    merged = make_chunk(
        chunk_id="merged",
        section_id="sec_general",
        section_path=["1 General"],
        section_ids=["sec_general", "sec_17", "sec_18"],
        sequence_number=1,
    )
    index = DocumentChunkIndex.build([merged])

    assert index.by_section_id["sec_general"] == [merged]
    assert index.by_section_id["sec_17"] == [merged]
    assert index.by_section_id["sec_18"] == [merged]


def test_plausible_candidates_finds_merged_chunk_when_anchor_is_a_folded_subsection() -> (
    None
):
    merged = make_chunk(
        chunk_id="merged",
        section_id="sec_general",
        section_path=["1 General"],
        section_ids=["sec_general", "sec_17", "sec_18"],
        sequence_number=1,
    )
    # A plain, unmerged chunk whose own primary section is exactly one of
    # the subsections folded into `merged`.
    anchor = make_chunk(
        chunk_id="anchor",
        section_id="sec_18",
        section_path=["1 General", "1.8 Liability and Warranty"],
        sequence_number=50,
    )
    index = DocumentChunkIndex.build([merged, anchor])

    candidates = index.plausible_candidates(anchor, neighbor_window=0)

    assert merged in candidates


def test_plausible_candidates_uses_anchors_own_touched_sections_when_it_is_the_merged_chunk() -> (
    None
):
    merged_anchor = make_chunk(
        chunk_id="merged",
        section_id="sec_general",
        section_path=["1 General"],
        section_ids=["sec_general", "sec_17", "sec_18"],
        sequence_number=1,
    )
    sibling_of_18 = make_chunk(
        chunk_id="sibling",
        section_id="sec_18",
        section_path=["1 General", "1.8 Liability and Warranty"],
        sequence_number=50,
    )
    index = DocumentChunkIndex.build([merged_anchor, sibling_of_18])

    candidates = index.plausible_candidates(merged_anchor, neighbor_window=0)

    assert sibling_of_18 in candidates


def test_chunk_without_section_ids_falls_back_to_its_primary_section_id() -> None:
    plain = make_chunk(
        chunk_id="plain",
        section_id="sec_overview",
        section_path=["Overview"],
        sequence_number=1,
    )
    index = DocumentChunkIndex.build([plain])

    assert index.by_section_id["sec_overview"] == [plain]
