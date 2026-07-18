from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata


class ChunkCrossReferenceType(StrEnum):
    PAGE_REFERENCE = "page_reference"
    # Detected and persisted for corpus visibility, but never resolved in
    # v1 -- resolving "see section 8.9"/"chap. 8.13.2" requires fuzzy
    # matching against section numbering/titles, a materially different and
    # riskier mechanism than a page lookup, deliberately deferred to a
    # follow-up phase once the page-based path is proven end-to-end.
    SECTION_REFERENCE = "section_reference"


class ChunkCrossReferenceResolutionStatus(StrEnum):
    RESOLVED_UNIQUE = "resolved_unique"
    RESOLVED_AMBIGUOUS = "resolved_ambiguous"
    UNRESOLVED = "unresolved"


@dataclass(slots=True)
class ChunkCrossReference:
    cross_reference_id: str
    document_id: str
    source_chunk_id: str

    reference_type: ChunkCrossReferenceType
    matched_text: str

    # Populated for PAGE_REFERENCE; None for SECTION_REFERENCE (which has no
    # page number to resolve against in v1).
    target_page: int | None = None
    # Populated for SECTION_REFERENCE (e.g. "8.9"); kept for future
    # section-based resolution and present-day corpus visibility.
    target_section_label: str | None = None

    target_chunk_id: str | None = None
    resolution_status: ChunkCrossReferenceResolutionStatus = (
        ChunkCrossReferenceResolutionStatus.UNRESOLVED
    )
    confidence_score: float = 0.0

    audit: AuditMetadata = field(default_factory=AuditMetadata)
