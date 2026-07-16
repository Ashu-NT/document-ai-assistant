from enum import StrEnum


class TableKind(StrEnum):
    """Single, shared vocabulary of "what kind of table is this," used at
    every stage that needs to name a table kind: parse-time subject-matter
    classification (formerly `TableCategory`), parse-time structural-shape
    classification (formerly `TableShape`), and the QA-time resolved
    answer-routing decision (formerly `ResolvedTableType`).

    Category and shape remain independent facts about a table (stored in
    `TableAsset.table_category`/`table_shape`, two separate fields) -- this
    enum only unifies the shared value vocabulary those two axes and the
    QA-time resolution draw from, so a value like "toc_table" or
    "general_table" is declared exactly once instead of three times.
    """

    GENERAL_TABLE = "general_table"
    RECORD_TABLE = "record_table"
    KEY_VALUE_TABLE = "key_value_table"
    TOC_TABLE = "toc_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    CERTIFICATION_TABLE = "certification_table"
    MAINTENANCE_INTERVAL_TABLE = "maintenance_interval_table"
    MAINTENANCE_SCHEDULE_TABLE = "maintenance_schedule_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    SPECIFICATION_MATRIX = "specification_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
    OPERATION_REFERENCE_TABLE = "operation_reference_table"
    TECHNICAL_DATA_TABLE = "technical_data_table"
    IDENTIFIER_TABLE = "identifier_table"
    CONNECTION_TABLE = "connection_table"
    SENSOR_INSTRUMENT_TABLE = "sensor_instrument_table"
    OPERATING_LIMITS_TABLE = "operating_limits_table"
