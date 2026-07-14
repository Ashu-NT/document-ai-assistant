from enum import StrEnum


class TableShape(StrEnum):
    GENERAL_TABLE = "general_table"
    RECORD_TABLE = "record_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
