from enum import StrEnum


class TableCategory(StrEnum):
    """Single-valued semantic subject of a table, set once at parse time by
    TableSemanticClassifier. Independent of TableShape (structural
    organization) and TableQueryStrategy (QA-time routing).
    """

    GENERAL_TABLE = "general_table"
    TOC_TABLE = "toc_table"
    MAINTENANCE_INTERVAL_TABLE = "maintenance_interval_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    OPERATION_REFERENCE_TABLE = "operation_reference_table"
    OPERATING_LIMITS_TABLE = "operating_limits_table"
    TECHNICAL_DATA_TABLE = "technical_data_table"
    CERTIFICATION_TABLE = "certification_table"
    CONNECTION_TABLE = "connection_table"
    SENSOR_INSTRUMENT_TABLE = "sensor_instrument_table"
    IDENTIFIER_TABLE = "identifier_table"
