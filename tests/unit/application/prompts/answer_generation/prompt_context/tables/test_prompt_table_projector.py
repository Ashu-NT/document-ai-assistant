from src.application.prompts.answer_generation.prompt_context.models import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.tables import (
    PromptTableProjector,
)


def test_build_projects_table_with_headers_rows_and_provenance() -> None:
    source = PromptSourceView(
        source_number=3,
        chunk_id="chunk_spec_001",
        chunk_name="Technical Data",
        chunk_type="technical_specification",
        document_title="Certificate",
        section_path="Certificate > Particulars",
        page_start=5,
        page_end=5,
        retrieval_source="dense",
        table_rows=[["Parameter", "Value"], ["Test pressure", "700 bar"]],
    )

    tables = PromptTableProjector().build([source])

    assert len(tables) == 1
    assert tables[0].table_id == "chunk_spec_001:table"
    assert tables[0].table_type == "certification_table"
    assert tables[0].source_number == 3
    assert tables[0].headers == ["Parameter", "Value"]
    assert tables[0].rows[0].cells == ["Test pressure", "700 bar"]
    assert tables[0].rows[0].cells_by_header == {
        "Parameter": "Test pressure",
        "Value": "700 bar",
    }


def test_build_skips_sources_without_table_rows() -> None:
    source = PromptSourceView(
        source_number=4,
        chunk_id="chunk_empty_001",
        content="No table here",
    )

    tables = PromptTableProjector().build([source])

    assert tables == []
