from src.application.contracts.pdf_links import PdfLinkExtractionResult
from src.application.workflows.parsing.builders.document_graph.cross_references.cross_reference_linking_outcome import (
    CrossReferenceLinkingOutcome,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_linker import (
    ChunkCrossReferenceLinker,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.pdf_link_cross_reference_linker import (
    PdfLinkCrossReferenceLinker,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.reconciliation.cross_reference_reconciliation_service import (
    CrossReferenceReconciliationService,
)
from src.domain.document import DocumentGraph
from src.domain.document.entities import ChunkCrossReferenceType

_LOCATION_TYPES = frozenset(
    {
        ChunkCrossReferenceType.PAGE_REFERENCE,
        ChunkCrossReferenceType.SECTION_REFERENCE,
    }
)


class CrossReferencePipeline:
    """Orchestrates the fuzzy linker, the native linker (if enabled), and
    reconciliation between them. Returns a plain CrossReferenceLinkingOutcome
    for DocumentGraphBuilder to add to the graph - never mutates `graph`
    itself, matching both linkers' and the reconciliation service's own
    purity.

    TABLE_REFERENCE/FIGURE_REFERENCE fuzzy candidates never enter
    reconciliation (no native equivalent competes for asset references) -
    they pass straight through to the canonical output untouched.
    """

    def __init__(
        self,
        *,
        reconciliation_service: CrossReferenceReconciliationService,
        fuzzy_linker: ChunkCrossReferenceLinker | None = None,
        native_linker: PdfLinkCrossReferenceLinker | None = None,
    ) -> None:
        self.fuzzy_linker = fuzzy_linker
        self.reconciliation_service = reconciliation_service
        self.native_linker = native_linker

    def run(
        self,
        graph: DocumentGraph,
        pdf_link_extraction_result: PdfLinkExtractionResult | None = None,
    ) -> CrossReferenceLinkingOutcome:
        fuzzy_references = (
            self.fuzzy_linker.link(graph) if self.fuzzy_linker is not None else []
        )
        location_type_fuzzy = [
            reference
            for reference in fuzzy_references
            if reference.reference_type in _LOCATION_TYPES
        ]
        asset_type_fuzzy = [
            reference
            for reference in fuzzy_references
            if reference.reference_type not in _LOCATION_TYPES
        ]

        native_result = None
        if self.native_linker is not None and pdf_link_extraction_result is not None:
            native_result = self.native_linker.link(graph, pdf_link_extraction_result)

        reconciliation_result = self.reconciliation_service.reconcile(
            location_type_fuzzy_references=location_type_fuzzy,
            native_result=native_result,
        )

        return CrossReferenceLinkingOutcome(
            evidence=reconciliation_result.evidence,
            canonical_references=(
                reconciliation_result.canonical_references + asset_type_fuzzy
            ),
            native_diagnostics=(
                native_result.diagnostics if native_result is not None else None
            ),
            reconciliation_diagnostics=reconciliation_result.diagnostics,
        )


__all__ = ["CrossReferencePipeline"]
