from enum import StrEnum


class ExtractionPromptType(StrEnum):
    IDENTIFIER = "identifier"
    MANUFACTURER = "manufacturer"
    SUPPLIER = "supplier"
    CONTACT_POINT = "contact_point"
    EQUIPMENT = "equipment"
    SPARE_PART = "spare_part"
    SPECIFICATION = "specification"
    MAINTENANCE_TASK = "maintenance_task"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    PROCEDURE = "procedure"
    SAFETY_WARNING = "safety_warning"
    TROUBLESHOOTING = "troubleshooting"
