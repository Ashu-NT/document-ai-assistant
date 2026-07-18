from __future__ import annotations

from src.domain.common import ChunkType
from src.domain.document.entities.chunk import DocumentChunk

# Shared between page- and section-based resolution: when several chunks
# are plausible targets, a chunk that actually contains procedure/
# troubleshooting content is a better landing point for "see page/section
# X" than a general/overview chunk that merely happens to fall in the same
# range.
_PROCEDURE_LIKE_CHUNK_TYPES = frozenset(
    {
        ChunkType.MAINTENANCE_PROCEDURE,
        ChunkType.OPERATION_INSTRUCTION,
        ChunkType.INSTALLATION_INSTRUCTION,
        ChunkType.TROUBLESHOOTING,
    }
)


def pick_best_candidate(candidates: list[DocumentChunk]) -> DocumentChunk:
    """Final tie-break once a resolver has narrowed to a candidate pool:
    prefer a procedure-like chunk_type, then the earliest sequence_number
    (the first content in reading order, typically the start of whatever
    the reference points to)."""
    procedure_like = [
        chunk for chunk in candidates if chunk.chunk_type in _PROCEDURE_LIKE_CHUNK_TYPES
    ]
    pool = procedure_like or candidates
    return min(pool, key=lambda chunk: chunk.sequence_number)


__all__ = ["pick_best_candidate"]
