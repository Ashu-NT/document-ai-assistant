from src.application.services.ai.chunk_embedding_enricher import enrich_embedding_text
from src.domain.common import ChunkType


def test_enrich_embedding_text_prefers_rows_based_headers_over_regex() -> None:
    content = (
        "Table caption text.\n\n"
        "| Part No | Description |\n"
        "|---|---|\n"
        "| HP-001 | Filter |"
    )
    # Rows disagree with the markdown text's own header labels, so the test
    # can prove which source actually won.
    table_rows = [["Part Number", "Denomination"], ["HP-001", "Filter"]]

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["Spare Parts"],
        content=content,
        table_rows=table_rows,
    )

    assert "Table headers: Part Number, Denomination" in result
    assert "Table headers: Part No, Description" not in result


def test_enrich_embedding_text_preserves_caption_and_context_from_markdown_scan() -> None:
    content = (
        "Spare parts for the hydraulic pump.\n\n"
        "| Part No | Description |\n"
        "|---|---|\n"
        "| HP-001 | Filter |"
    )
    table_rows = [["Part No", "Description"], ["HP-001", "Filter"]]

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["Spare Parts"],
        content=content,
        table_rows=table_rows,
    )

    assert "Table caption: Spare parts for the hydraulic pump." in result
    assert "Table headers: Part No, Description" in result


def test_enrich_embedding_text_adds_section_component_framing_for_general_chunks() -> (
    None
):
    content = "Replace the hydraulic filter as described."

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.GENERAL,
        section_path=["Maintenance", "Hydraulic Pump", "Filter Replacement"],
        content=content,
    )

    assert "Section: Filter Replacement" in result
    assert "Component: Hydraulic Pump" in result


def test_enrich_embedding_text_adds_generic_related_terms_for_general_chunks() -> None:
    content = "Grease the shaft seal every 500 operating hours."

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.GENERAL,
        section_path=["Lubrication"],
        content=content,
    )

    assert "Related terms:" in result
    assert "lubrication interval" in result


def test_enrich_embedding_text_omits_chunk_type_specific_aliases_for_general_chunks() -> (
    None
):
    content = "Disconnect power before servicing the unit."

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.GENERAL,
        section_path=["Safety"],
        content=content,
    )

    # "hazard"/"safety warning" aliases are SAFETY_WARNING-specific and
    # should not appear on an unrelated GENERAL chunk just because it
    # happens to be about a safety-adjacent topic.
    assert "hazard" not in result
    assert "safety warning" not in result


def test_enrich_embedding_text_falls_back_to_regex_when_no_table_rows() -> None:
    content = (
        "| Part No | Description |\n"
        "|---|---|\n"
        "| HP-001 | Filter |"
    )

    result = enrich_embedding_text(
        base_text=content,
        chunk_type=ChunkType.SPARE_PARTS_TABLE,
        section_path=["Spare Parts"],
        content=content,
    )

    assert "Table headers: Part No, Description" in result
