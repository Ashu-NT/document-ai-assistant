from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    *,
    content: str,
    chunk_id: str = "chunk_001",
    section_path: list[str] | None = None,
    section_title: str | None = None,
    page_start: int | None = 45,
    page_end: int | None = 46,
    chunk_type: ChunkType = ChunkType.SPARE_PARTS_TABLE,
) -> RetrievedChunk:
    citation = (
        Citation(citation_id=f"cit_{chunk_id}", document_id="doc_1", section_title=section_title)
        if section_title
        else None
    )
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=section_path or ["7 Components", "Spare Parts"],
        source=SourceLocation(page_start=page_start, page_end=page_end),
        citation=citation,
    )


def test_render_returns_none_for_unsupported_intent() -> None:
    renderer = SparePartsListRenderer()

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[_make_chunk(content="| Position | Qty |\n| 1 | 2 |")],
    )

    assert result is None


def test_render_returns_none_when_no_spare_parts_chunks_present() -> None:
    renderer = SparePartsListRenderer()

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk(content="no rows", chunk_type=ChunkType.GENERAL)],
    )

    assert result is None


def test_render_never_denies_spare_parts_list_when_evidence_exists() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
        "| 2 | 1 | O-ring | A00181 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "no spare part" not in result.lower()
    assert "not found" not in result.lower()
    assert result.startswith("Spare parts lists found:")


def test_render_groups_rows_by_section_and_page() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[
            _make_chunk(
                content=content,
                section_title="Spare Parts List",
                section_path=["7 Components", "Spare Parts"],
                page_start=45,
                page_end=46,
            )
        ],
    )

    assert result is not None
    assert "1. Spare Parts List" in result
    assert "Pages: 45-46" in result
    assert "Section: 7 Components > Spare Parts" in result
    assert "Type: spare_parts_table" in result
    assert "Available rows:" in result
    assert "- Position: 1" in result
    assert "Quantity: 2" in result
    assert "Denomination: Filter" in result
    assert "Spare Part No.: A00103" in result


def test_render_multiple_chunks_produce_multiple_numbered_groups() -> None:
    renderer = SparePartsListRenderer()
    chunk_a = _make_chunk(
        chunk_id="chunk_a",
        content=(
            "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
            "|---|---|---|---|\n"
            "| 1 | 2 | Filter | A00103 |\n"
        ),
        section_title="Exploded Views and Spare Parts List for the Disposer",
        page_start=45,
        page_end=46,
    )
    chunk_b = _make_chunk(
        chunk_id="chunk_b",
        content=(
            "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
            "|---|---|---|---|\n"
            "| 14.00 | 1 | Pump Casing | 70.00 |\n"
        ),
        section_title="Vacuum / Transfer Pump Assembly - Spare Parts List",
        page_start=85,
        page_end=87,
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[chunk_a, chunk_b],
    )

    assert result is not None
    assert "1. Exploded Views and Spare Parts List for the Disposer" in result
    assert "2. Vacuum / Transfer Pump Assembly - Spare Parts List" in result


def test_render_marks_unparseable_table_content_as_partial() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "Take Note: Use of original manufacturer spare parts and accessories "
        "is in the interest of system performance and safety."
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert result.startswith("Spare parts lists found:")
    assert "Only partial table content was available in the retrieved context." in result
    assert "not found" not in result.lower()


def test_render_returns_none_when_question_does_not_mention_spare_parts() -> None:
    renderer = SparePartsListRenderer()

    result = renderer.render(
        question="what is the design pressure?",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk(content="| Position | Qty |\n| 1 | 2 |")],
    )

    assert result is None


def test_render_defers_to_llm_when_export_format_requested() -> None:
    renderer = SparePartsListRenderer()

    result = renderer.render(
        question="export the spare parts list as csv",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk(content="| Position | Qty |\n| 1 | 2 |")],
    )

    assert result is None
