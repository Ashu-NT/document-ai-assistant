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


def test_build_preserves_structured_table_metadata_and_uses_shape_signal() -> None:
    source = PromptSourceView(
        source_number=5,
        chunk_id="chunk_sched_001",
        chunk_type="maintenance_interval",
        table_rows=[["Task", "Weekly"], ["Inspect filter", "x"]],
        table_shape="maintenance_schedule_matrix",
        table_structure_quality=0.94,
        table_header_paths=[["Task"], ["Interval", "Weekly"]],
        table_axis_summary={"row_axis": "task", "column_axis": "interval"},
        metadata={"table_category": "maintenance_interval_table"},
    )

    tables = PromptTableProjector().build([source])

    assert len(tables) == 1
    assert tables[0].table_type == "maintenance_table"
    assert tables[0].table_shape == "maintenance_schedule_matrix"
    assert tables[0].table_structure_quality == 0.94
    assert tables[0].header_paths == [["Task"], ["Interval", "Weekly"]]
    assert tables[0].axis_summary == {
        "row_axis": "task",
        "column_axis": "interval",
    }


def test_build_uses_specification_matrix_shape_for_prompt_table_type() -> None:
    source = PromptSourceView(
        source_number=6,
        chunk_id="chunk_spec_matrix",
        chunk_type="technical_specification",
        table_rows=[
            ["Parameter", "Compact version", "Remote version", "Unit"],
            ["Pressure range", "0...10", "0...16", "bar"],
        ],
        table_shape="specification_matrix",
        metadata={"table_category": "technical_data_table"},
    )

    tables = PromptTableProjector().build([source])

    assert len(tables) == 1
    assert tables[0].table_type == "specification_table"
    assert tables[0].table_shape == "specification_matrix"
