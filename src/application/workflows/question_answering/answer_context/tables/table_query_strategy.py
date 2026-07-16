from enum import StrEnum


class TableQueryStrategy(StrEnum):
    """QA-time-only resolution of "how should this specific table be
    answered," derived from category + shape + chunk_type + header/row
    content signals. Never persisted -- recomputed per query against
    AnswerTable/PromptSourceView. Not an intrinsic property of the table
    itself.
    """

    GENERAL_TABLE = "general_table"
    RECORD_TABLE = "record_table"
    KEY_VALUE_TABLE = "key_value_table"
    TOC_TABLE = "toc_table"
    TROUBLESHOOTING_TABLE = "troubleshooting_table"
    SPARE_PARTS_TABLE = "spare_parts_table"
    CERTIFICATION_TABLE = "certification_table"
    MAINTENANCE_SCHEDULE_TABLE = "maintenance_schedule_table"
    MAINTENANCE_SCHEDULE_MATRIX = "maintenance_schedule_matrix"
    SPECIFICATION_MATRIX = "specification_matrix"
    PERFORMANCE_CURVE_MATRIX = "performance_curve_matrix"
