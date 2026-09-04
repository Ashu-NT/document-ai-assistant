from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata
from src.domain.document.entities.cross_reference_reconciliation_outcome import (
    CrossReferenceReconciliationOutcome,
)
from src.domain.document.entities.pdf_link_provenance import PdfLinkProvenance


class ChunkCrossReferenceType(StrEnum):
    PAGE_REFERENCE = "page_reference"
    # Resolved via ChunkSectionReferenceResolver against the numeric prefix
    # in each chunk's section_path titles (e.g. "8.9 Lubrication oil").
    SECTION_REFERENCE = "section_reference"
    # Resolved via ChunkAssetReferenceResolver against the leading number in
    # a table/picture asset's caption (e.g. "Table 3. Spare parts"). Falls
    # back to UNRESOLVED when the document doesn't caption its tables with a
    # number, which is expected and not an error - table/figure numbering
    # conventions vary a lot across source documents.
    TABLE_REFERENCE = "table_reference"
    FIGURE_REFERENCE = "figure_reference"
    # Resolved via PdfLinkCrossReferenceLinker from a same-document PDF GOTO
    # link annotation - exact structural evidence, not text-derived.
    PDF_LINK_REFERENCE = "pdf_link_reference"


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
    # Populated for TABLE_REFERENCE/FIGURE_REFERENCE (e.g. "3" from "see
    # Table 3").
    target_asset_label: str | None = None

    target_chunk_id: str | None = None
    resolution_status: ChunkCrossReferenceResolutionStatus = (
        ChunkCrossReferenceResolutionStatus.UNRESOLVED
    )
    confidence_score: float = 0.0

    # Populated for PDF_LINK_REFERENCE rows, and for CONFIRMED rows where a
    # native evidence row corroborated the target regardless of which type
    # won the canonical label (see CrossReferenceReconciliationService).
    link_provenance: PdfLinkProvenance | None = None

    # Set only when this canonical row was produced by reconciling fuzzy and
    # native candidates (see CrossReferenceReconciliationOutcome). None for
    # every row with no cross-source counterpart, which is the majority case.
    reconciliation_outcome: CrossReferenceReconciliationOutcome | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)
