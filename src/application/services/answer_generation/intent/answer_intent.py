from enum import StrEnum


class AnswerIntent(StrEnum):
    GENERAL = "general"
    SPECIFICATION_SUMMARY = "specification_summary"
    MAINTENANCE_SUMMARY = "maintenance_summary"
    PROCEDURE_STEPS = "procedure_steps"
    SAFETY_WARNINGS = "safety_warnings"
    TROUBLESHOOTING = "troubleshooting"
    CERTIFICATION_SUMMARY = "certification_summary"
    IDENTIFIER_LOOKUP = "identifier_lookup"
    TABLE_SUMMARY = "table_summary"
    DOCUMENT_SUMMARY = "document_summary"
