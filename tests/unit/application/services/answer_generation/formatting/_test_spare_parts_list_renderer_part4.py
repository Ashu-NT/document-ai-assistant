import json

from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.workflows.question_answering.answer_context.structured_source_builder import (
    StructuredSourceBuilder,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table_projector import (
    AnswerTableProjector,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_source_with_rows(
    *,
    content: str,
    table_rows: list[list[str]],
    table_category: str,
    chunk_id: str = "chunk_001",
):
    chunk = RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["7 Components", "Spare Parts List"],
        source=SourceLocation(page_start=85, page_end=87),
        citation=Citation(
            citation_id=f"cit_{chunk_id}",
            document_id="doc_1",
            section_title="Spare Parts List",
        ),
        metadata={
            "table_rows_json": json.dumps(table_rows),
            "table_category": table_category,
        },
    )
    return StructuredSourceBuilder().build_sources([chunk])[0]


def test_render_uses_normalized_answer_tables_before_raw_source_reparse() -> None:
    renderer = SparePartsListRenderer()
    source = _make_source_with_rows(
        content="Spare parts list content was flattened badly in raw retrieval text.",
        table_category="spare_parts_table",
        table_rows=[
            [
                "Part Pos. Qty Unit",
                "Designation Size / Dimension, Material / Surface",
                "Part No",
                "",
            ],
            ["0010 1 Pce", "housing", "", ""],
            ["", "0115 1 Pce drive shaft", "", ""],
            ["14.00 Pump Casing", "70.00 Lantern bracket", "", ""],
        ],
    )
    tables = AnswerTableProjector().build([source])

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[source],
        tables=tables,
    )

    assert result is not None
    assert "housing" in result
    assert "0115" in result
    assert "drive shaft" in result
    assert "14.00" in result
    assert "70.00" in result
    assert renderer.last_diagnostics()["spare_parts_partial"] is False


def test_render_skips_non_spare_parts_answer_tables_even_if_chunk_type_matches() -> None:
    renderer = SparePartsListRenderer()
    source = _make_source_with_rows(
        content="Maintenance Intervals table.",
        table_category="maintenance_interval_table",
        table_rows=[
            ["Description", "Interval", "Refers to"],
            ["Cleaning of the machine", "After daily use", ""],
        ],
    )
    tables = AnswerTableProjector().build([source])

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[],
        tables=tables,
    )

    assert result is None
