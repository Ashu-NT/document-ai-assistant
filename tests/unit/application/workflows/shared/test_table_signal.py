from src.application.workflows.shared.table_signal import TableSignal


def test_table_signal_has_the_expected_multi_valued_members() -> None:
    assert {member.value for member in TableSignal} == {
        "identifiers",
        "specifications",
        "operating_limits",
        "maintenance_intervals",
        "schedules",
        "troubleshooting",
        "spare_parts",
        "certification",
        "connections",
        "sensor_data",
        "performance_data",
    }
