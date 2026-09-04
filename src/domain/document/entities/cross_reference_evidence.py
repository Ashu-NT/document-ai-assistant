from dataclasses import dataclass, field

from src.domain.common import AuditMetadata
from src.domain.document.entities.chunk_cross_reference import (
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
)
from src.domain.document.entities.cross_reference_reconciliation_outcome import (
    CrossReferenceReconciliationOutcome,
)
from src.domain.document.entities.pdf_link_provenance import PdfLinkProvenance


@dataclass(slots=True)
class CrossReferenceEvidence:
    """One fuzzy PAGE_REFERENCE/SECTION_REFERENCE or native PDF_LINK_REFERENCE
    candidate considered by CrossReferenceReconciliationService. Append-only
    within a document's lifecycle (see repository/migration notes) - never
    updated after insert, never read by retrieval. TABLE_REFERENCE/
    FIGURE_REFERENCE candidates never become evidence; they pass straight to
    the canonical ChunkCrossReference table untouched.

    Every canonical ChunkCrossReference row traces back to one or more
    evidence rows via canonical_cross_reference_id; a CONFLICT or
    UNRECONCILED_MULTI_CANDIDATE group's evidence rows all have that field
    set to None, since no canonical row was created for them.
    """

    evidence_id: str
    document_id: str
    source_chunk_id: str

    reference_type: ChunkCrossReferenceType
    matched_text: str

    target_page: int | None = None
    target_section_label: str | None = None

    target_chunk_id: str | None = None
    resolution_status: ChunkCrossReferenceResolutionStatus = (
        ChunkCrossReferenceResolutionStatus.UNRESOLVED
    )
    confidence_score: float = 0.0

    link_provenance: PdfLinkProvenance | None = None

    reconciliation_outcome: CrossReferenceReconciliationOutcome | None = None
    # Shared by every evidence row compared together in one reconciliation
    # decision (e.g. the fuzzy and native rows behind a single CONFLICT).
    reconciliation_group_id: str | None = None
    # The canonical ChunkCrossReference row this evidence is associated
    # with, if any. Named for what it points at, not for the evidence having
    # "won": a losing ACCEPTED_* candidate or one side of a CONFIRMED pair is
    # still associated with the canonical decision without having been the
    # shape chosen for it.
    canonical_cross_reference_id: str | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)


__all__ = ["CrossReferenceEvidence"]
