from enum import StrEnum


class TableShape(StrEnum):
    """Single-valued structural organization of a table, set once at parse
    time by TableStructureSummaryBuilder. `None` on TableAsset.table_shape
    means no summarizer matched -- there is no catch-all member here, matching
    that behavior exactly.
    """

    RECORD_TABLE = "record_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    SPECIFICATION_MATRIX = "specification_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
