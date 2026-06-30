from enum import StrEnum


class RetrievalQueryIntent(StrEnum):
    DOCUMENT_EXPLORATION = "document_exploration"
    IDENTIFIER = "identifier"
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    OVERVIEW = "overview"
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY = "safety"
    TABLE = "table"
    FIGURE = "figure"
    SPECIFICATION = "specification"
