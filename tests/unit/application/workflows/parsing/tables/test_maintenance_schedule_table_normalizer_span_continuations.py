from src.application.workflows.parsing.tables.normalization.maintenance_schedule_table_normalizer import (
    MaintenanceScheduleTableNormalizer,
)
from src.domain.assets.table_cell_span import TableCellSpan


def test_normalize_merges_span_backed_wrapped_schedule_task_and_notes() -> None:
    normalized = MaintenanceScheduleTableNormalizer().normalize(
        [
            ["Task", "D", "W", "Notes"],
            ["Inspect the pump and", "x", "", "Refer to"],
            ["clean the housing", "", "", "Section 4"],
        ],
        table_category="maintenance_interval_table",
        chunk_type=None,
        cell_spans=[
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=0,
                col_end=0,
                text="Inspect the pump and clean the housing",
                raw_lines=["Inspect the pump and", "clean the housing"],
            ),
            TableCellSpan(
                row_start=1,
                row_end=2,
                col_start=3,
                col_end=3,
                text="Refer to Section 4",
                raw_lines=["Refer to", "Section 4"],
            ),
        ],
    )

    assert normalized is not None
    assert normalized.headers == ["Task", "Daily", "Weekly", "Notes"]
    assert normalized.rows == [
        ["Inspect the pump and clean the housing", "x", "", "Refer to Section 4"],
    ]


def test_normalize_does_not_merge_schedule_rows_without_span_evidence() -> None:
    normalized = MaintenanceScheduleTableNormalizer().normalize(
        [
            ["Task", "D", "W", "Notes"],
            ["Inspect the pump and", "x", "", "Refer to"],
            ["clean the housing", "", "", "Section 4"],
        ],
        table_category="maintenance_interval_table",
        chunk_type=None,
        cell_spans=None,
    )

    assert normalized is not None
    assert normalized.headers == ["Task", "Daily", "Weekly", "Notes"]
    assert normalized.rows == [
        ["Inspect the pump and", "x", "", "Refer to"],
        ["clean the housing", "", "", "Section 4"],
    ]
