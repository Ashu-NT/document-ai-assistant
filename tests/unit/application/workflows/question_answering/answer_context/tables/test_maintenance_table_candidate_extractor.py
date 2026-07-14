from src.application.workflows.question_answering.answer_context.maintenance.maintenance_table_candidate_extractor import (
    MaintenanceTableCandidateExtractor,
)
from src.application.workflows.question_answering.answer_context.tables import (
    AnswerTable,
    AnswerTableRow,
)


def test_extractor_accepts_semantic_rowwise_projection_from_matrix_tables() -> None:
    extractor = MaintenanceTableCandidateExtractor()
    table = AnswerTable(
        source_number=1,
        chunk_id="chunk_maintenance",
        chunk_type="maintenance_interval",
        document_title=None,
        section_path=None,
        page_start=None,
        page_end=None,
        headers=["Task", "Interval", "Component", "Notes"],
        rows=[
            AnswerTableRow(
                source_row_index=1,
                cells=[
                    "Inspect basket",
                    "Daily; Monthly",
                    "Basket",
                    "Before startup",
                ],
            )
        ],
        table_kind="maintenance_schedule_matrix",
        column_roles={
            0: "task",
            1: "interval",
            2: "component",
            3: "notes",
        },
    )

    candidates = extractor.extract(table)

    assert len(candidates) == 1
    assert candidates[0].task == "Inspect basket"
    assert candidates[0].interval == "Daily; Monthly"
    assert candidates[0].component == "Basket"
    assert candidates[0].notes == "Before startup"
