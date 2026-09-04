from dataclasses import dataclass, field

from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkLinkingDiagnostics,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation.cross_reference_reconciliation_result import (
    CrossReferenceReconciliationDiagnostics,
)
from src.domain.document.entities import ChunkCrossReference, CrossReferenceEvidence


@dataclass(slots=True, frozen=True)
class CrossReferenceLinkingOutcome:
    """What CrossReferencePipeline.run() returns to DocumentGraphBuilder -
    the two collections it mutates the graph with, plus diagnostics for
    logging. Neither collection has been added to `graph` yet; that remains
    DocumentGraphBuilder's sole responsibility."""

    evidence: list[CrossReferenceEvidence] = field(default_factory=list)
    canonical_references: list[ChunkCrossReference] = field(default_factory=list)
    native_diagnostics: PdfLinkLinkingDiagnostics | None = None
    reconciliation_diagnostics: CrossReferenceReconciliationDiagnostics = field(
        default_factory=CrossReferenceReconciliationDiagnostics
    )


__all__ = ["CrossReferenceLinkingOutcome"]
