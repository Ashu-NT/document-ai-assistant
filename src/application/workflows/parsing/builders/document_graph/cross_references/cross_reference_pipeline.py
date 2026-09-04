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
from src.config.logging import get_logger
from src.domain.document import DocumentGraph
from src.domain.document.entities import ChunkCrossReferenceType
from src.shared.observability.stage_logger import StageLogScope, time_stage

_logger = get_logger(__name__)

_LOCATION_TYPES = frozenset(
    {
        ChunkCrossReferenceType.PAGE_REFERENCE,
        ChunkCrossReferenceType.SECTION_REFERENCE,
    }
)


def _warn_on_conflicts_and_ambiguity(scope: StageLogScope) -> str | None:
    conflict_count = scope.counts.get("conflict_count", 0)
    unreconciled_count = scope.counts.get("unreconciled_multi_candidate_chunks", 0)
    if not conflict_count and not unreconciled_count:
        return None
    return (
        f"conflict_count={conflict_count} "
        f"unreconciled_multi_candidate_chunks={unreconciled_count} "
        "(recoverable: neither is trusted over the other without bbox "
        "matching, so no canonical row was created for these - see "
        "outputs/architecture/pdf_link_cross_reference_plan.md)"
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
        with time_stage(
            _logger,
            "cross_reference_pipeline",
            document_id=graph.document.document_id,
            warn_if=_warn_on_conflicts_and_ambiguity,
        ) as scope:
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
            if (
                self.native_linker is not None
                and pdf_link_extraction_result is not None
            ):
                native_result = self.native_linker.link(
                    graph, pdf_link_extraction_result
                )

            reconciliation_result = self.reconciliation_service.reconcile(
                location_type_fuzzy_references=location_type_fuzzy,
                native_result=native_result,
            )

            outcome = CrossReferenceLinkingOutcome(
                evidence=reconciliation_result.evidence,
                canonical_references=(
                    reconciliation_result.canonical_references + asset_type_fuzzy
                ),
                native_diagnostics=(
                    native_result.diagnostics if native_result is not None else None
                ),
                reconciliation_diagnostics=reconciliation_result.diagnostics,
            )

            scope.counts.update(
                {
                    "fuzzy_candidates": len(fuzzy_references),
                    "native_annotations": (
                        len(pdf_link_extraction_result.annotations)
                        if pdf_link_extraction_result is not None
                        else 0
                    ),
                    "evidence_rows": len(outcome.evidence),
                    "canonical_rows": len(outcome.canonical_references),
                    "single_source_count": (
                        reconciliation_result.diagnostics.single_source_count
                    ),
                    "confirmed_count": reconciliation_result.diagnostics.confirmed_count,
                    "accepted_textual_count": (
                        reconciliation_result.diagnostics.accepted_textual_count
                    ),
                    "accepted_native_count": (
                        reconciliation_result.diagnostics.accepted_native_count
                    ),
                    "conflict_count": reconciliation_result.diagnostics.conflict_count,
                    "unreconciled_multi_candidate_chunks": (
                        reconciliation_result.diagnostics.unreconciled_multi_candidate_chunks
                    ),
                }
            )

        return outcome


__all__ = ["CrossReferencePipeline"]
