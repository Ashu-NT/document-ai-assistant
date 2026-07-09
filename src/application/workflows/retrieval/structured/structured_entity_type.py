from enum import StrEnum


class StructuredEntityType(StrEnum):
    MANUFACTURER = "manufacturer"
    SUPPLIER = "supplier"
    CONTACT_POINT = "contact_point"
    SPARE_PART = "spare_part"
    EQUIPMENT = "equipment"
    MAINTENANCE_TASK = "maintenance_task"
    PROCEDURE = "procedure"
    SPECIFICATION = "specification"
    SAFETY_WARNING = "safety_warning"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    TROUBLESHOOTING = "troubleshooting"
