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
    FOOTNOTE = "footnote"
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
    CODE_BLOCK = "code_block"
    FORMULA = "formula"
    FORM_DATA = "form_data"
    GENERAL = "general"
    UNKNOWN = "unknown"


class IdentifierType(StrEnum):
    PART_NUMBER = "part_number"
    SERIAL_NUMBER = "serial_number"
    MODEL_NUMBER = "model_number"
    PRODUCT_NAME = "product_name"
    DRAWING_NUMBER = "drawing_number"
    COMPONENT_CODE = "component_code"
    CERTIFICATE_NUMBER = "certificate_number"
    MANUFACTURER_NAME = "manufacturer_name"
    SUPPLIER_NAME = "supplier_name"
    PHONE_NUMBER = "phone_number"
    FAX_NUMBER = "fax_number"
    EMAIL_ADDRESS = "email_address"
    URL = "url"
    UNKNOWN = "unknown"


class IngestionStatus(StrEnum):
    PENDING = "pending"
    PARSING = "parsing"
    REGISTERED = "registered"
    CLASSIFIED = "classified"
    FINALIZED = "finalized"
    EXTRACTED = "extracted"
    EMBEDDED = "embedded"
    INDEXED = "indexed"
    COMPLETE = "complete"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED_FILE_DUPLICATE = "skipped_file_duplicate"
    SKIPPED_CONTENT_DUPLICATE = "skipped_content_duplicate"
    REDIRECTED_STALE_PARSER_VERSION = "redirected_stale_parser_version"
