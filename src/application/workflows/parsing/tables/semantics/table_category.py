from enum import StrEnum


class TableCategory(StrEnum):
    TOC_TABLE = "toc_table"
    MAINTENANCE_INTERVAL_TABLE = "maintenance_interval_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    OPERATION_REFERENCE_TABLE = "operation_reference_table"
    TECHNICAL_DATA_TABLE = "technical_data_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    CERTIFICATION_TABLE = "certification_table"
    IDENTIFIER_TABLE = "identifier_table"
    CONNECTION_TABLE = "connection_table"
    SENSOR_INSTRUMENT_TABLE = "sensor_instrument_table"
    OPERATING_LIMITS_TABLE = "operating_limits_table"
    GENERAL_TABLE = "general_table"
