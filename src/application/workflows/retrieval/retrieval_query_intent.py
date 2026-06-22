from enum import StrEnum


class RetrievalQueryIntent(StrEnum):
    IDENTIFIER = "identifier"
    GENERAL = "general"
    OVERVIEW = "overview"
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY = "safety"
    TABLE = "table"
    FIGURE = "figure"
    SPECIFICATION = "specification"
