from src.application.workflows.shared.table_shape import TableShape


def test_table_shape_has_exactly_the_summarizer_reachable_members() -> None:
    assert {member.value for member in TableShape} == {
        "record_table",
        "maintenance_schedule_matrix",
        "specification_matrix",
        "performance_curve_matrix",
    }
