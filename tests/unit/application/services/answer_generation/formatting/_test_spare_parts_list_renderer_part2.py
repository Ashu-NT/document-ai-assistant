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

def test_render_skips_bare_quantity_unit_artifact_rows() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| | Pce | | |\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Quantity: Pce" not in result
    assert "Description: Filter" in result
    assert "Part No.: A00103" in result
    assert "Only partial row content was available in the retrieved context." in result

def test_render_extracts_pid_style_valve_rows_with_part_no() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| P&ID Pos Nr. Service Function Type Part No. |\n"
        "|---|\n"
        "| V.00.01.01 Dry Running Protection Solenoid G1/2 2/2-way, 24Vdc A00103 |\n"
        "| V.00.02.03 Discharge Overboard / Ashore Blank Flange Fitted |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[
            _make_source(
                content=content,
                section_title="Valve List > Spare Parts",
                section_path=["7 Components", "Valve List", "Spare Parts"],
                page_start=97,
                page_end=97,
            )
        ],
    )

    assert result is not None
    assert "P&ID Position: V.00.01.01" in result
    assert "Part No.: A00103" in result
    assert "Dry Running Protection" in result

def test_render_excludes_safety_section_without_real_table_rows() -> None:
    renderer = SparePartsListRenderer()
    safety_content = (
        "Only original spare parts and equipment authorised by FMD are "
        "suitable and safe for use. Incorrect or faulty spare parts can "
        "lead to damage, malfunction or complete breakdown of the equipment."
    )
    valve_content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )
    safety_chunk = _make_source(
        chunk_id="chunk_safety",
        content=safety_content,
        section_title="2.8 Spare Parts",
        section_path=["2 Safety", "2.8 Spare Parts"],
        page_start=11,
        page_end=11,
    )
    valve_chunk = _make_source(
        chunk_id="chunk_valve",
        content=valve_content,
        section_title="Spare Parts List",
        page_start=97,
        page_end=97,
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[safety_chunk, valve_chunk],
    )

    assert result is not None
    assert "2.8 Spare Parts" not in result
    assert "Pages: 11" not in result
    assert "Spare Parts List" in result
    assert "Part No.: A00103" in result

def test_render_layout_a_structured_header_table() -> None:
    renderer = SparePartsListRenderer()
    content = (
        "| Position No: | Qty: | Designation: | Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter | A00103 |\n"
    )

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Position: 1" in result
    assert "Quantity: 2" in result
    assert "Description: Filter" in result
    assert "Part No.: A00103" in result

def test_render_layout_a_free_form_position_quantity_unit_description() -> None:
    renderer = SparePartsListRenderer()
    content = "0010 1 Pce housing"

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Position: 0010" in result
    assert "Quantity: 1" in result
    assert "Unit: Pce" in result
    assert "Description: housing" in result
    assert "Part No." not in result

def test_render_layout_b_pid_valve_style_row() -> None:
    renderer = SparePartsListRenderer()
    content = "V.00.01.01 Dry Running Protection Solenoid G1/2 2/2-way 24Vdc A00103"

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "P&ID Position: V.00.01.01" in result
    assert "Service: Dry Running Protection" in result
    assert "Type: Solenoid G1/2 2/2-way 24Vdc" in result
    assert "Part No.: A00103" in result

def test_render_layout_c_two_column_exploded_view_pairs() -> None:
    renderer = SparePartsListRenderer()
    content = "14.00 Pump Casing 70.00 Lantern bracket"

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Position: 14.00" in result
    assert "Description: Pump Casing" in result
    assert "Position: 70.00" in result
    assert "Description: Lantern bracket" in result

def test_render_layout_d_falls_back_to_raw_row_for_unrecognized_shape() -> None:
    renderer = SparePartsListRenderer()
    content = "5 Filter Housing A00103 Yes"

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Raw row: 5 Filter Housing A00103 Yes" in result
    assert "Only partial row content was available in the retrieved context." in result

def test_render_does_not_invent_part_no_from_plain_quantity_like_token() -> None:
    renderer = SparePartsListRenderer()
    content = "V.00.02.03 Discharge Overboard Ashore Blank Flange Fitted"

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=content, section_title="Spare Parts List")],
    )

    assert result is not None
    assert "Part No." not in result
    assert "Flange Fitted" in result

def test_render_prefers_structured_entities_over_chunk_parsing() -> None:
    renderer = SparePartsListRenderer()
    chunk_content = (
        "| Position No: | Qty: | Denomination: | Spare Part No: |\n"
        "|---|---|---|---|\n"
        "| 1 | 2 | Filter (from chunk text) | Z99999 |\n"
    )
    entities = [
        {
            "_entity_type": "spare_part",
            "part_number": "A00103",
            "description": "Filter (from extracted data)",
            "quantity": "2",
            "component_name": "Pump",
            "manufacturer_name": "Acme",
        }
    ]

    result = renderer.render(
        question="table of spare part list",
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        sources=[_make_source(content=chunk_content, section_title="Spare Parts List")],
        resolved_structured_entities=entities,
    )

    assert result is not None
    assert "Filter (from extracted data)" in result
    assert "Part No.: A00103" in result
    assert "Component: Pump" in result
    assert "Manufacturer: Acme" in result
    # The regex-parsed chunk content must not appear -- structured data wins.
    assert "Z99999" not in result
    assert "from chunk text" not in result
