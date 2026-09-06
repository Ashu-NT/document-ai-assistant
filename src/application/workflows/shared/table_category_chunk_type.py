from src.application.workflows.shared.table_category import TableCategory
from src.domain.common import ChunkType


_CATEGORY_CHUNK_TYPES = {
    TableCategory.SPARE_PARTS_TABLE.value: ChunkType.SPARE_PARTS_TABLE,
    TableCategory.MAINTENANCE_INTERVAL_TABLE.value: ChunkType.MAINTENANCE_INTERVAL,
    TableCategory.TROUBLESHOOTING_TABLE.value: ChunkType.TROUBLESHOOTING,
    TableCategory.OPERATION_REFERENCE_TABLE.value: ChunkType.OPERATION_INSTRUCTION,
    TableCategory.TECHNICAL_DATA_TABLE.value: ChunkType.TECHNICAL_SPECIFICATION,
    TableCategory.OPERATING_LIMITS_TABLE.value: ChunkType.TECHNICAL_SPECIFICATION,
    TableCategory.CERTIFICATION_TABLE.value: ChunkType.CERTIFICATION_INFO,
}


def chunk_type_for_table_category(
    table_category: str | TableCategory | None,
) -> ChunkType | None:
    normalized = str(table_category or "").strip().lower()
    return _CATEGORY_CHUNK_TYPES.get(normalized)
