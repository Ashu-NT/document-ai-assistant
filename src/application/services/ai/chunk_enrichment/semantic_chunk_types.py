from src.domain.common import ChunkType

ENRICHED_CHUNK_TYPES: frozenset[ChunkType] = frozenset(
    {
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.MAINTENANCE_INTERVAL,
        ChunkType.SPARE_PARTS_TABLE,
        ChunkType.SAFETY_WARNING,
        ChunkType.TROUBLESHOOTING,
        ChunkType.TECHNICAL_SPECIFICATION,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.CERTIFICATION_INFO,
    }
)

_CHUNK_TYPE_LABELS: dict[ChunkType, str] = {
    ChunkType.MAINTENANCE_PROCEDURE: "maintenance procedure",
    ChunkType.MAINTENANCE_INTERVAL: "maintenance interval",
    ChunkType.SPARE_PARTS_TABLE: "spare parts table",
    ChunkType.SAFETY_WARNING: "safety warning",
    ChunkType.TROUBLESHOOTING: "troubleshooting",
    ChunkType.TECHNICAL_SPECIFICATION: "technical specification",
    ChunkType.INSTALLATION_INSTRUCTION: "installation instruction",
    ChunkType.OPERATION_INSTRUCTION: "operation instruction",
    ChunkType.CERTIFICATION_INFO: "certification information",
}


def chunk_type_label(chunk_type: ChunkType) -> str | None:
    return _CHUNK_TYPE_LABELS.get(chunk_type)
