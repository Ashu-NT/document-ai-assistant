from __future__ import annotations

from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.services.document import (
    DeterministicIdentifierScanner,
    DocumentLookupService,
    DocumentRegistrationService,
    IdentifierPromotionService,
)
from src.application.workflows.classification import (
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion.ingestion_exceptions import (
    DocumentNotFoundForReingestionError,
    IngestionWorkflowError,
    ReingestionNotSupportedError,
)
from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus
from src.application.workflows.linking import SemanticLinkingWorkflow
from src.shared.activity import ActivityContext
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress


class ExtractionRetryStep:
    """Retries only the extraction (+ identifier + semantic-linking) stage
    for a document whose chunks/classification already succeeded but whose
    extraction never completed - e.g. a prior ingestion run raised
    mid-batch-extraction, leaving the document committed (its
    `documents`/`chunks`/`sections` rows survive the stage commits that
    happen before extraction starts) with no `extraction_results` row.

    Unlike reingestion, this does not re-parse the source file, replace the
    document graph, or re-embed chunks - all of that already succeeded and
    is left untouched. It exists so a partial-extraction failure can be
    repaired in place, without the cost of a full reingest and without
    minting a new document_id.

    If the stored document graph contains sections/elements but no final
    chunks, this first re-runs post-classification chunk finalization in
    place (without embedding) and then continues with the extraction retry.
    If a saved extraction result already exists with unresolved chunk IDs,
    only that unresolved subset is retried and then merged back into the
    persisted result.
    """

    def __init__(
        self,
        *,
        document_lookup_service: DocumentLookupService | None,
        post_classification_chunk_finalization_workflow: (
            PostClassificationChunkFinalizationWorkflow
        ),
        extraction_workflow: ExtractionWorkflow,
        document_registration_service: DocumentRegistrationService,
        id_generator: IdGenerator,
        unit_of_work: UnitOfWork,
        extraction_enabled: bool = True,
        identifier_promotion_service: IdentifierPromotionService | None = None,
        deterministic_identifier_scanner: DeterministicIdentifierScanner | None = None,
        semantic_linking_workflow: SemanticLinkingWorkflow | None = None,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.post_classification_chunk_finalization_workflow = (
            post_classification_chunk_finalization_workflow
        )
        self.extraction_workflow = extraction_workflow
        self.document_registration_service = document_registration_service
        self.id_generator = id_generator
        self.unit_of_work = unit_of_work
        self.extraction_enabled = extraction_enabled
        self.identifier_promotion_service = identifier_promotion_service
        self.deterministic_identifier_scanner = deterministic_identifier_scanner
        self.semantic_linking_workflow = semantic_linking_workflow

    def run(
        self,
        document_id: str,
        *,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        if self.document_lookup_service is None:
            raise ReingestionNotSupportedError(
                "Retrying extraction requires a document_lookup_service "
                "dependency, which this IngestionWorkflow instance was not "
                "constructed with.",
                error_code="reingestion_not_supported",
                details={"document_id": document_id},
            )
        if not self.extraction_enabled:
            raise IngestionWorkflowError(
                "Retrying extraction is disabled by config.",
                error_code="ingestion.extraction.disabled",
                details={"document_id": document_id},
            )

        final_graph = self.document_lookup_service.get_document_graph(
            document_id,
            activity_context=activity_context,
        )
        if final_graph is None:
            raise DocumentNotFoundForReingestionError(
                "Document to retry extraction for does not exist.",
                error_code="reingestion.document_not_found",
                details={"document_id": document_id},
            )

        if not final_graph.chunks:
            if not final_graph.elements:
                raise IngestionWorkflowError(
                    "Document has no persisted elements or chunks to repair in place.",
                    error_code="ingestion.final_graph.empty",
                    details={"document_id": document_id},
                )
            emit_progress(
                progress_callback,
                (
                    "Document has persisted elements but no final chunks. "
                    "Rebuilding final chunk set in place before retrying extraction..."
                ),
            )
            final_graph = self.post_classification_chunk_finalization_workflow.finalize(
                document_id,
                embed_final_chunks=False,
                activity_context=activity_context,
                progress_callback=progress_callback,
            )
            if not final_graph.chunks:
                raise IngestionWorkflowError(
                    "Recovered finalization still produced no chunks for extraction.",
                    error_code="ingestion.final_graph.no_chunks",
                    details={
                        "document_id": document_id,
                        "element_count": len(final_graph.elements),
                        "section_count": len(final_graph.sections),
                    },
                )

        extraction_service = getattr(self.extraction_workflow, "extraction_service", None)
        existing_extraction_result = (
            extraction_service.get_document_extraction_result(document_id)
            if extraction_service is not None
            else None
        )
        retry_chunks = list(final_graph.chunks.values())
        if (
            existing_extraction_result is not None
            and existing_extraction_result.unresolved_chunk_ids
        ):
            unresolved_chunk_ids = set(existing_extraction_result.unresolved_chunk_ids)
            retry_chunks = [
                chunk
                for chunk in final_graph.chunks.values()
                if chunk.chunk_id in unresolved_chunk_ids
            ]
            if not retry_chunks:
                raise IngestionWorkflowError(
                    "Saved unresolved extraction chunk IDs no longer exist in the final document graph.",
                    error_code="ingestion.extraction.unresolved_chunks_missing",
                    details={
                        "document_id": document_id,
                        "unresolved_chunk_ids": list(
                            existing_extraction_result.unresolved_chunk_ids
                        ),
                    },
                )
            emit_progress(
                progress_callback,
                (
                    "Retrying only unresolved extraction chunks: "
                    f"{len(retry_chunks)} chunk(s)."
                ),
            )
        else:
            existing_extraction_result = None

        emit_progress(progress_callback, "Extraction started.")
        extraction_result = self.extraction_workflow.extract(
            document_id,
            retry_chunks,
            activity_context=activity_context,
            progress_callback=progress_callback,
            replace_existing=True,
            tables=final_graph.tables,
            sections=final_graph.sections,
            base_result=existing_extraction_result,
        )
        self.unit_of_work.commit()

        if self.identifier_promotion_service is not None:
            promoted_identifiers = self.identifier_promotion_service.promote(
                extraction_result=extraction_result,
                document_graph=final_graph,
                id_generator=self.id_generator,
            )
            if promoted_identifiers:
                for identifier in promoted_identifiers:
                    final_graph.identifiers[identifier.identifier_id] = identifier
                self.document_registration_service.register_document_identifiers(
                    promoted_identifiers,
                    activity_context=activity_context,
                )
                self.unit_of_work.commit()
        if self.deterministic_identifier_scanner is not None:
            existing_normalized = {
                (i.normalized_value or "", i.identifier_type.value)
                for i in final_graph.identifiers.values()
            }
            scanned_identifiers = self.deterministic_identifier_scanner.scan(
                final_graph,
                self.id_generator,
                existing_normalized=existing_normalized,
            )
            if scanned_identifiers:
                for identifier in scanned_identifiers:
                    final_graph.identifiers[identifier.identifier_id] = identifier
                self.document_registration_service.register_document_identifiers(
                    scanned_identifiers,
                    activity_context=activity_context,
                )
                self.unit_of_work.commit()

        semantic_relationship_count = None
        if self.semantic_linking_workflow is not None:
            semantic_relationships = self.semantic_linking_workflow.link(document_id)
            semantic_relationship_count = len(semantic_relationships)
            self.unit_of_work.commit()

        emit_progress(progress_callback, "Extraction completed.")
        return IngestionResult(
            status=IngestionStatus.EXTRACTED,
            document_id=document_id,
            file_name=final_graph.document.file_name,
            document_type=final_graph.document.document_type.value,
            chunk_count=len(final_graph.chunks),
            current_stage=IngestionStage.EXTRACTION,
            diagnostics={
                "extraction_id": extraction_result.extraction_id,
                "maintenance_task_count": len(extraction_result.maintenance_tasks),
                "spare_part_count": len(extraction_result.spare_parts),
                "unresolved_chunk_count": len(extraction_result.unresolved_chunk_ids),
                "semantic_relationship_count": semantic_relationship_count,
            },
        )
