from src.application.workflows.parsing.tables.normalization.maintenance_schedule_table_normalizer import (
    MaintenanceScheduleTableNormalizer,
)

_COMPACT_SCHEDULE_ROWS = [
    ["D", "Q Q", "M S A", "Task Reference"],
    ["General Maintenance Work on the Press"],
    ["X", "General visual inspection daily or after period of particularly high load"],
    ["", "X", "Clean dirt from the housing", "See gearbox Annex"],
]


def test_normalize_expands_compact_schedule_matrix_for_maintenance_interval_category() -> None:
    normalized = MaintenanceScheduleTableNormalizer().normalize(
        _COMPACT_SCHEDULE_ROWS,
        table_category="maintenance_interval_table",
        chunk_type=None,
    )

    assert normalized is not None
    assert normalized.headers == [
        "Daily",
        "Quarterly",
        "Monthly",
        "Semi-Annual",
        "Annual",
        "Task",
        "Notes",
    ]
    assert normalized.rows[1] == [
        "x",
        "",
        "",
        "",
        "",
        "General visual inspection daily or after period of particularly high load",
        "",
    ]


def test_normalize_returns_none_for_unrelated_category() -> None:
    normalized = MaintenanceScheduleTableNormalizer().normalize(
        _COMPACT_SCHEDULE_ROWS,
        table_category="technical_data_table",
        chunk_type=None,
    )

    assert normalized is None


def test_normalize_returns_none_when_fewer_than_two_schedule_columns() -> None:
    normalized = MaintenanceScheduleTableNormalizer().normalize(
        [["Task", "Notes"], ["Inspect filter", "Routine check"]],
        table_category="maintenance_interval_table",
        chunk_type=None,
    )

    assert normalized is None
