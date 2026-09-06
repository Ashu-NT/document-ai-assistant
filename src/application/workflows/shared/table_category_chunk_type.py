from src.application.workflows.shared.table_category import TableCategory
from src.domain.common import ChunkType


def chunk_type_for_table_category(
    table_category: str | TableCategory | None,
) -> ChunkType | None:
    normalized = str(table_category or "").strip().lower()
    mapping = {
        TableCategory.SPARE_PARTS_TABLE: ChunkType.SPARE_PARTS_TABLE,
        TableCategory.MAINTENANCE_INTERVAL_TABLE: ChunkType.MAINTENANCE_INTERVAL,
        TableCategory.TROUBLESHOOTING_TABLE: ChunkType.TROUBLESHOOTING,
        TableCategory.OPERATION_REFERENCE_TABLE: ChunkType.OPERATION_INSTRUCTION,
        TableCategory.TECHNICAL_DATA_TABLE: ChunkType.TECHNICAL_SPECIFICATION,
        TableCategory.OPERATING_LIMITS_TABLE: ChunkType.TECHNICAL_SPECIFICATION,
        TableCategory.CERTIFICATION_TABLE: ChunkType.CERTIFICATION_INFO,
    }
    return mapping.get(normalized)
