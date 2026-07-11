from src.application.prompts.answer_generation.prompt_context.models import (
    PromptSourceView,
    PromptTableRowView,
    PromptTableView,
)
from src.application.prompts.answer_generation.prompt_context.topology import (
    PromptEvidenceTopologyBuilder,
)
from src.application.services.answer_generation import AnswerIntent


def test_build_assigns_direct_supporting_and_contextual_roles() -> None:
    sources = [
        PromptSourceView(
            source_number=1,
            chunk_id="chunk_interval",
            chunk_type="maintenance_interval",
            section_path="Maintenance > Intervals",
            page_start=58,
            page_end=58,
        ),
        PromptSourceView(
            source_number=2,
            chunk_id="chunk_overview",
            chunk_type="overview",
            section_path="Maintenance > Overview",
            page_start=56,
            page_end=56,
        ),
        PromptSourceView(
            source_number=3,
            chunk_id="chunk_general",
            chunk_type="general",
            section_path="Maintenance > Intervals",
            page_start=59,
            page_end=59,
        ),
    ]

    source_families, section_topology = PromptEvidenceTopologyBuilder().build(
        answer_intent_value=AnswerIntent.MAINTENANCE_SUMMARY.value,
        sources=sources,
        tables=[],
    )

    assert source_families[0].direct_source_numbers == [1]
    assert source_families[0].supporting_source_numbers == [3]
    assert source_families[1].contextual_source_numbers == [2]
    assert section_topology[0].section_name == "Intervals"
    assert section_topology[0].direct_source_numbers == [1]
    assert section_topology[0].supporting_source_numbers == [3]
    assert section_topology[1].parent_section_path == "Maintenance"


def test_build_marks_table_sources_as_direct_for_table_driven_intents() -> None:
    source = PromptSourceView(
        source_number=4,
        chunk_id="chunk_table",
        chunk_type="technical_specification",
        section_path="Certificate > Particulars",
        page_start=5,
        page_end=5,
        table_rows=[["Parameter", "Value"], ["Test pressure", "700 bar"]],
    )
    tables = [
        PromptTableView(
            table_id="chunk_table:table",
            table_type="certification_table",
            source_number=4,
            chunk_id="chunk_table",
            chunk_type="technical_specification",
            section_path="Certificate > Particulars",
            page_start=5,
            page_end=5,
            headers=["Parameter", "Value"],
            rows=[
                PromptTableRowView(
                    source_row_index=1,
                    cells=["Test pressure", "700 bar"],
                    cells_by_header={
                        "Parameter": "Test pressure",
                        "Value": "700 bar",
                    },
                )
            ],
        )
    ]

    source_families, section_topology = PromptEvidenceTopologyBuilder().build(
        answer_intent_value=AnswerIntent.TABLE_SUMMARY.value,
        sources=[source],
        tables=tables,
    )

    assert source_families[0].direct_source_numbers == [4]
    assert source_families[0].table_source_numbers == [4]
    assert section_topology[0].table_source_numbers == [4]
