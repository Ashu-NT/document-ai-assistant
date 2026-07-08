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
