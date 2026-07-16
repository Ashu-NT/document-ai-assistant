from src.application.workflows.shared.table_category import TableCategory


def test_table_category_has_exactly_the_classifier_reachable_members() -> None:
    assert {member.value for member in TableCategory} == {
        "general_table",
        "toc_table",
        "maintenance_interval_table",
        "troubleshooting_table",
        "spare_parts_table",
        "operation_reference_table",
        "operating_limits_table",
        "technical_data_table",
        "certification_table",
        "connection_table",
        "sensor_instrument_table",
        "identifier_table",
    }
