from enum import StrEnum


class TableColumnSemanticRole(StrEnum):
    """Generic, small semantic-role vocabulary for a table COLUMN (not a
    whole table -- see TableCategory/TableShape for that). Deliberately
    limited to roles already observed live in this codebase's existing
    Q&A-side column-role resolver (AnswerTableSchemaInferer /
    table_header_semantics._HEADER_ROLE_ALIASES) -- not an open-ended
    engineering ontology. Expanding this vocabulary requires real, reviewed
    evidence of recurring need across multiple real tables, not a single
    document's shape.
    """

    LABEL = "label"
    VALUE = "value"
    TASK = "task"
    INTERVAL = "interval"
    COMPONENT = "component"
    NOTES = "notes"
    POSITION = "position"
    QUANTITY = "quantity"
    UNIT = "unit"
    PART_NO = "part_no"
    SERVICE = "service"
    TYPE = "type"
