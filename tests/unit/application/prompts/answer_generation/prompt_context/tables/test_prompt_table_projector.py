from src.application.prompts.answer_generation.prompt_context.models import (
    PromptSourceView,
)
from src.application.prompts.answer_generation.prompt_context.tables import (
    PromptTableProjector,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
    AnswerTableRow,
)
from src.application.workflows.question_answering.answer_context.tables.table_query_strategy import (
    TableQueryStrategy,
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
    assert tables[0].table_strategy == "key_value_table"
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
    assert tables[0].table_strategy == "maintenance_schedule_matrix"
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
    assert tables[0].table_strategy == "specification_matrix"
    assert tables[0].table_shape == "specification_matrix"


def test_build_from_answer_tables_preserves_typed_table_projection() -> None:
    answer_table = AnswerTable(
        source_number=8,
        chunk_id="chunk_maint_001",
        chunk_type="maintenance_interval",
        document_title="FWC12 Manual",
        section_path="Maintenance > Schedule",
        page_start=58,
        page_end=59,
        headers=["Task", "Interval", "Component"],
        rows=[
            AnswerTableRow(
                source_row_index=1,
                cells=["Replace filter", "Every 500 hours", "Hydraulic pump"],
                cells_by_header={
                    "Task": "Replace filter",
                    "Interval": "Every 500 hours",
                    "Component": "Hydraulic pump",
                },
            )
        ],
        table_kind=TableQueryStrategy.MAINTENANCE_SCHEDULE_TABLE,
        logical_table_family_id="table_family_001",
        table_category="maintenance_interval_table",
        table_shape="maintenance_schedule_table",
        table_structure_quality=0.96,
        header_paths=[["Task"], ["Interval"], ["Component"]],
        axis_summary={"row_axis": "task", "column_axis": "interval"},
    )

    tables = PromptTableProjector().build_from_answer_tables([answer_table])

    assert len(tables) == 1
    assert tables[0].table_id == "table_family_001"
    assert tables[0].table_type == "maintenance_table"
    assert tables[0].table_strategy == "maintenance_schedule_table"
    assert tables[0].document_title == "FWC12 Manual"
    assert tables[0].headers == ["Task", "Interval", "Component"]
    assert tables[0].rows[0].cells_by_header == {
        "Task": "Replace filter",
        "Interval": "Every 500 hours",
        "Component": "Hydraulic pump",
    }
