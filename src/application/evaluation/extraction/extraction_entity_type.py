from enum import StrEnum


class ExtractionEntityType(StrEnum):
    """The exact production structured-extraction entity types (see
    `src/domain/extraction/`). Phase 2B evaluates only these - no
    evaluation-only entity types (e.g. CertificationInfo, ToolingRequirement)
    are ever introduced here."""

    MAINTENANCE_TASK = "maintenance_task"
    SPARE_PART = "spare_part"
    EQUIPMENT_INFO = "equipment_info"
    MANUFACTURER = "manufacturer"
    SUPPLIER = "supplier"
    CONTACT_POINT = "contact_point"
    PROCEDURE = "procedure"
    SPECIFICATION = "specification"
    SAFETY_WARNING = "safety_warning"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    TROUBLESHOOTING_ENTRY = "troubleshooting_entry"
    EXTRACTED_IDENTIFIER = "extracted_identifier"
