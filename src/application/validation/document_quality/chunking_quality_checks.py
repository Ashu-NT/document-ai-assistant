from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.validation.document_quality.quality_check_result import (
    QualityCheckResult,
)

if TYPE_CHECKING:
    from src.domain.common import ChunkType
    from src.domain.document import DocumentChunk

_MAX_GENERAL_CHUNK_RATIO = 0.6
_MAINTENANCE_HEADING_MARKERS = (
    "maintenance",
    "servicing",
    "service interval",
    "cleaning",
    "replacement",
    "lubrication",
)
_MAINTENANCE_CHUNK_TYPES = frozenset(
    ["maintenance_procedure", "maintenance_interval"]
)


def check_general_chunk_ratio(chunks: list[DocumentChunk]) -> QualityCheckResult:
    name = "chunking.general_chunk_ratio"
    if not chunks:
        return QualityCheckResult.ok(name)
    general_count = sum(
        1 for c in chunks if getattr(c, "chunk_type", None) and
        str(getattr(c, "chunk_type", "")).lower() in ("general", "chunktype.general")
    )
    ratio = general_count / len(chunks)
    if ratio > _MAX_GENERAL_CHUNK_RATIO:
        return QualityCheckResult.warn(
            name,
            f"Excessive GENERAL chunks: {ratio:.1%} ({general_count}/{len(chunks)})",
            details={"general_count": general_count, "total": len(chunks), "ratio": ratio},
        )
    return QualityCheckResult.ok(name)


def check_chunks_have_section_paths(chunks: list[DocumentChunk]) -> QualityCheckResult:
    name = "chunking.chunks_missing_section_path"
    if not chunks:
        return QualityCheckResult.ok(name)
    missing = [
        c for c in chunks
        if not getattr(c, "section_path", None)
    ]
    ratio = len(missing) / len(chunks)
    if ratio > 0.3:
        return QualityCheckResult.warn(
            name,
            f"{ratio:.1%} of chunks have no section path",
            details={"missing_count": len(missing), "total": len(chunks)},
        )
    return QualityCheckResult.ok(name)


def check_maintenance_headings_have_chunks(
    chunks: list[DocumentChunk],
) -> QualityCheckResult:
    name = "chunking.maintenance_headings_without_chunks"
    has_maintenance_heading = any(
        any(
            marker in " ".join(getattr(c, "section_path", []) or []).lower()
            for marker in _MAINTENANCE_HEADING_MARKERS
        )
        for c in chunks
    )
    if not has_maintenance_heading:
        return QualityCheckResult.ok(name)
    has_maintenance_chunks = any(
        str(getattr(c, "chunk_type", "")).lower().split(".")[-1]
        in _MAINTENANCE_CHUNK_TYPES
        for c in chunks
    )
    if not has_maintenance_chunks:
        return QualityCheckResult.warn(
            name,
            "Document has maintenance section headings but no maintenance chunk types",
            details={"maintenance_markers_checked": list(_MAINTENANCE_HEADING_MARKERS)},
        )
    return QualityCheckResult.ok(name)
