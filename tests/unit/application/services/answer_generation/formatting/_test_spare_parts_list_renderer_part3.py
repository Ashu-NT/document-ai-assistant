from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)

from src.application.services.answer_generation.formatting.spare_parts_table_parser import (
    SPARE_PARTS_TABLE_PARSER_RULES_VERSION,
)

from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)

from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
)

from src.application.workflows.question_answering.answer_context.structured_source_builder import (
    StructuredSourceBuilder,
)

from src.domain.common import ChunkType

from src.domain.common.source_location import SourceLocation

from src.domain.retrieval.citation import Citation

from src.domain.retrieval.retrieved_chunk import RetrievedChunk

def _make_source(
    *,
    content: str,
    chunk_id: str = "chunk_001",
    section_path: list[str] | None = None,
    section_title: str | None = None,
    page_start: int | None = 45,
    page_end: int | None = 46,
    chunk_type: ChunkType = ChunkType.SPARE_PARTS_TABLE,
    metadata: dict[str, str] | None = None,
) -> AnswerSource:
    """Builds a RetrievedChunk with the same shape the old chunk-based tests
    used, then runs it through the real StructuredSourceBuilder -- so these
    tests exercise a production-faithful AnswerSource (pre-decoded
    table_rows, computed chunk_name/section_path) instead of hand-rolling a
    second, potentially-diverging mapping in the test fixture."""
    citation = (
        Citation(citation_id=f"cit_{chunk_id}", document_id="doc_1", section_title=section_title)
        if section_title
        else None
    )
    chunk = RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=chunk_type,
        section_path=section_path or ["7 Components", "Spare Parts"],
        source=SourceLocation(page_start=page_start, page_end=page_end),
        citation=citation,
        metadata=metadata or {},
    )
    return StructuredSourceBuilder().build_sources([chunk])[0]

def test_render_falls_back_to_chunk_parsing_when_no_structured_entities() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
        resolved_structured_entities=[],
    )

    assert result is not None
    assert "Part No." in result
    assert "A00103" in result

def test_render_ignores_structured_entities_of_other_types() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )
    entities = [
        {"_entity_type": "manufacturer", "manufacturer_name": "Acme"},
    ]

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
        resolved_structured_entities=entities,
    )

    # Non-spare-part entities are ignored, so it falls back to chunk parsing.
    assert result is not None
    assert "Part No." in result
    assert "A00103" in result

def test_render_skips_structured_entities_missing_part_number_and_description() -> None:
    renderer = SparePartsListRenderer()
    entities = [
        {"_entity_type": "spare_part", "quantity": "2", "component_name": "Pump"},
    ]

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content="no table evidence here")],
        resolved_structured_entities=entities,
    )

    assert result is None

def test_render_prefers_table_rows_json_over_chunk_text_regex_parsing() -> None:
    renderer = SparePartsListRenderer()
    chunk_content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter (from chunk text) | Z99999 |\n"
    )
    import json

    metadata = {
        "table_rows_json": json.dumps(
            [
                ["Position No", "Qty", "Denomination", "Spare Part No"],
                ["1", "2", "Filter (from rows)", "A00103"],
            ]
        )
    }

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[
            _make_source(
                content=chunk_content,
                section_title="Spare Parts List",
                metadata=metadata,
            )
        ],
    )

    assert result is not None
    assert "Filter (from rows)" in result
    assert "Part No." in result
    assert "A00103" in result
    assert "Z99999" not in result
    assert "from chunk text" not in result

def test_render_falls_back_to_chunk_parsing_when_table_rows_json_has_no_header() -> None:
    renderer = SparePartsListRenderer()
    chunk_content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )
    import json

    metadata = {
        "table_rows_json": json.dumps(
            [["Unrecognized", "Columns"], ["foo", "bar"]]
        )
    }

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[
            _make_source(
                content=chunk_content,
                section_title="Spare Parts List",
                metadata=metadata,
            )
        ],
    )

    assert result is not None
    assert "Part No." in result
    assert "A00103" in result

def test_render_falls_back_to_chunk_parsing_when_table_rows_json_malformed() -> None:
    renderer = SparePartsListRenderer()
    chunk_content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[
            _make_source(
                content=chunk_content,
                section_title="Spare Parts List",
                metadata={"table_rows_json": "not valid json"},
            )
        ],
    )

    assert result is not None
    assert "Part No." in result
    assert "A00103" in result
