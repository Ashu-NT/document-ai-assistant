from enum import StrEnum


class DocumentType(StrEnum):
    MANUAL = "manual"
    DATASHEET = "datasheet"
    DRAWING = "drawing"
    CERTIFICATE = "certificate"
    REPORT = "report"
    UNKNOWN = "unknown"


class ElementType(StrEnum):
    TITLE = "title"
    SECTION_HEADER = "section_header"
    TEXT = "text"
    LIST_ITEM = "list_item"
    TABLE = "table"
    PICTURE = "picture"
    CAPTION = "caption"
    KEY_VALUE = "key_value"
    FORM = "form"
    CODE = "code"
    FORMULA = "formula"
    UNKNOWN = "unknown"


class ChunkType(StrEnum):
    OVERVIEW = "overview"
    MAINTENANCE_PROCEDURE = "maintenance_procedure"
    MAINTENANCE_INTERVAL = "maintenance_interval"
    SPARE_PARTS_TABLE = "spare_parts_table"
    SAFETY_WARNING = "safety_warning"
    TROUBLESHOOTING = "troubleshooting"
    TECHNICAL_SPECIFICATION = "technical_specification"
    INSTALLATION_INSTRUCTION = "installation_instruction"
    OPERATION_INSTRUCTION = "operation_instruction"
    CERTIFICATION_INFO = "certification_info"
    DRAWING_REFERENCE = "drawing_reference"
    GENERAL = "general"
    UNKNOWN = "unknown"


class IdentifierType(StrEnum):
    PART_NUMBER = "part_number"
    SERIAL_NUMBER = "serial_number"
    MODEL_NUMBER = "model_number"
    DRAWING_NUMBER = "drawing_number"
    COMPONENT_CODE = "component_code"
    UNKNOWN = "unknown"


class IngestionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED_FILE_DUPLICATE = "skipped_file_duplicate"
    SKIPPED_CONTENT_DUPLICATE = "skipped_content_duplicate"
