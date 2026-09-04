from __future__ import annotations

from datetime import UTC
from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.services.document import (
    DeterministicIdentifierScanner,
    DocumentLookupService,
    DocumentRegistrationService,
    DuplicateDetectionService,
    IdentifierPromotionService,
)
from src.application.validation.document_quality import DocumentQualityGate
from src.application.validation.ingestion import IngestionRequestValidator
from src.application.workflows.classification import (
    DocumentClassificationWorkflow,
    PostClassificationChunkFinalizationWorkflow,
)
from src.application.workflows.embedding import EmbeddingWorkflow
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion.models.ingestion_exceptions import (
    IngestionWorkflowError,
    StaleParserVersionDetected,
)
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_result import IngestionResult
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.pipeline import (
    build_ingestion_workflow_pipeline,
)
from src.application.workflows.ingestion.models.reingestion_request import (
    ReingestionRequest,
)
from src.application.workflows.ingestion.runtime import (
    IngestionRuntimeCapabilities,
    IngestionRuntimeProfileResolver,
)
from src.application.workflows.linking import SemanticLinkingWorkflow
from src.application.workflows.parsing import ParsingWorkflow
from src.config.logging import get_logger
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.events import EventContext
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator
from src.shared.observability.stage_logger import time_stage

_logger = get_logger(__name__)

class IngestionWorkflow:
    def __init__(
        self,
        *,
        unit_of_work: UnitOfWork,
        ingestion_request_validator: IngestionRequestValidator,
        duplicate_detection_service: DuplicateDetectionService,
        parsing_workflow: ParsingWorkflow,
        document_registration_service: DocumentRegistrationService,
        document_classification_workflow: DocumentClassificationWorkflow,
        post_classification_chunk_finalization_workflow: (
            PostClassificationChunkFinalizationWorkflow
        ),
        extraction_workflow: ExtractionWorkflow,
        embedding_workflow: EmbeddingWorkflow,
        id_generator: IdGenerator,
        runtime_capabilities: IngestionRuntimeCapabilities | None = None,
        extraction_enabled: bool = True,
        classification_enabled: bool = True,
        quality_gate: DocumentQualityGate | None = None,
        identifier_promotion_service: IdentifierPromotionService | None = None,
        deterministic_identifier_scanner: DeterministicIdentifierScanner | None = None,
        document_lookup_service: DocumentLookupService | None = None,
        semantic_linking_workflow: SemanticLinkingWorkflow | None = None,
        activity_service=None,
        audit_service=None,
        event_service=None,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.ingestion_request_validator = ingestion_request_validator
        self.duplicate_detection_service = duplicate_detection_service
        self.parsing_workflow = parsing_workflow
        self.document_registration_service = document_registration_service
        self.document_classification_workflow = document_classification_workflow
        self.post_classification_chunk_finalization_workflow = (
            post_classification_chunk_finalization_workflow
        )
        self.extraction_workflow = extraction_workflow
        self.embedding_workflow = embedding_workflow
        self.id_generator = id_generator
        self.runtime_capabilities = runtime_capabilities or IngestionRuntimeProfileResolver().resolve(
            requested_profile=None,
            extraction_enabled=extraction_enabled,
            question_generation_enabled=False,
            deterministic_identifier_scan_enabled=(
                deterministic_identifier_scanner is not None
            ),
            semantic_linking_enabled=semantic_linking_workflow is not None,
            classification_enabled=classification_enabled,
        )
        self.extraction_enabled = self.runtime_capabilities.extraction_enabled
        self.classification_enabled = self.runtime_capabilities.classification_enabled
        self.quality_gate = quality_gate or DocumentQualityGate()
        self.identifier_promotion_service = identifier_promotion_service
        self.deterministic_identifier_scanner = (
            deterministic_identifier_scanner
            if self.runtime_capabilities.deterministic_identifier_scan_enabled
            else None
        )
        self.document_lookup_service = document_lookup_service
        self.semantic_linking_workflow = (
            semantic_linking_workflow
            if self.runtime_capabilities.semantic_linking_enabled
            else None
        )
        self.activity_service = activity_service
        self.audit_service = audit_service
        self.event_service = event_service

        self._pipeline = build_ingestion_workflow_pipeline(
            unit_of_work=self.unit_of_work,
            id_generator=self.id_generator,
            event_service=self.event_service,
            duplicate_detection_service=self.duplicate_detection_service,
            quality_gate=self.quality_gate,
            document_lookup_service=self.document_lookup_service,
            post_classification_chunk_finalization_workflow=(
                self.post_classification_chunk_finalization_workflow
            ),
            extraction_workflow=self.extraction_workflow,
            document_registration_service=self.document_registration_service,
            identifier_promotion_service=self.identifier_promotion_service,
            deterministic_identifier_scanner=self.deterministic_identifier_scanner,
            semantic_linking_workflow=self.semantic_linking_workflow,
            parsing_workflow=self.parsing_workflow,
            document_classification_workflow=(
                self.document_classification_workflow
            ),
            embedding_workflow=self.embedding_workflow,
            runtime_capabilities=self.runtime_capabilities,
            extraction_enabled=self.extraction_enabled,
            classification_enabled=self.classification_enabled,
            runtime_diagnostics_loader=self._runtime_diagnostics,
            question_generation_model_loader=self._question_generation_model,
            extraction_model_loader=self._extraction_model,
            ensure_final_graph_has_chunks=self._ensure_final_graph_has_chunks,
        )

    @tracked_action(
        action="document.ingestion.completed",
        entity_type="document",
        activity=True,
        audit=True,
        event=False,
    )
    def run(
        self,
        request: IngestionRequest,
        *,
        activity_context: ActivityContext | None = None,
        audit_context: AuditContext | None = None,
        event_context: EventContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        validation = self.ingestion_request_validator.validate(request)
        validation.raise_if_invalid()
        pipeline = self._pipeline

        bootstrap = pipeline.run_bootstrapper.bootstrap(
            request,
            activity_context=activity_context,
            audit_context=audit_context,
            event_context=event_context,
            progress_callback=progress_callback,
        )
        file_path = bootstrap.file_path
        file_name = bootstrap.file_name
        file_hash = bootstrap.file_hash
        content_hash = bootstrap.content_hash
        correlation_id = bootstrap.correlation_id
        ingestion_run = bootstrap.ingestion_run
        resolved_activity_context = bootstrap.activity_context
        resolved_event_context = bootstrap.event_context
        warnings = bootstrap.warnings
        stage_session = pipeline.stage_lifecycle.create_session(
            ingestion_run=ingestion_run,
            file_name=file_name,
            event_context=resolved_event_context,
            progress_callback=progress_callback,
        )

        current_stage = IngestionStage.DUPLICATE_CHECK
        with time_stage(
            _logger,
            "ingestion_workflow",
            document_id=ingestion_run.document_id,
            ingestion_run_id=ingestion_run.run_id,
        ) as scope:
            try:
                duplicate_result = pipeline.duplicate_coordinator.check_file_hash_duplicate(
                    request=request,
                    ingestion_run=ingestion_run,
                    file_name=file_name,
                    file_path=file_path,
                    file_hash=file_hash,
                    correlation_id=correlation_id,
                    warnings=warnings,
                    activity_context=resolved_activity_context,
                    event_context=resolved_event_context,
                    progress_callback=progress_callback,
                    current_parser_version=self.parsing_workflow.parser.parser_version,
                )
                if duplicate_result is not None:
                    scope.counts["outcome"] = "duplicate"
                    return duplicate_result
                result = pipeline.stage_sequence_executor.run(
                    request=request,
                    file_path=file_path,
                    file_name=file_name,
                    file_hash=file_hash,
                    content_hash=content_hash,
                    correlation_id=correlation_id,
                    ingestion_run=ingestion_run,
                    stage_session=stage_session,
                    activity_context=resolved_activity_context,
                    warnings=warnings,
                )
                scope.counts["outcome"] = "ingested"
                return result
            except StaleParserVersionDetected as exc:
                scope.counts["outcome"] = "stale_parser_reingest"
                return self.reingest(
                    ReingestionRequest(
                        document_id=exc.details["document_id"],
                        force=True,
                        preserve_document_id=True,
                        run_quality_checks=request.run_quality_checks,
                        requested_by=request.requested_by,
                        correlation_id=correlation_id,
                        file_path_override=file_path,
                    ),
                    activity_context=resolved_activity_context,
                    audit_context=audit_context,
                    progress_callback=progress_callback,
                )

    @tracked_action(
        action="document.reingestion.requested",
        entity_type="document",
        activity=True,
        audit=True,
        event=False,
    )
    def reingest(
        self,
        request: ReingestionRequest,
        *,
        activity_context: ActivityContext | None = None,
        audit_context: AuditContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        ingestion_request = self._pipeline.reingestion_step.prepare_request(
            request,
            activity_context=activity_context,
        )
        return self.run(
            ingestion_request,
            activity_context=activity_context,
            audit_context=audit_context,
            progress_callback=progress_callback,
        )

    def retry_extraction(
        self,
        document_id: str,
        *,
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        """Retry only the extraction (+ identifier + semantic-linking) stage
        for a document whose chunks/classification already succeeded but
        whose extraction never completed - e.g. a prior ingestion run
        raised mid-batch-extraction, leaving the document committed (its
        `documents`/`chunks`/`sections` rows survive the stage commits that
        happen before extraction starts) with no `extraction_results` row.

        Unlike `reingest`, this does not re-parse the source file, replace
        the document graph, or re-embed chunks - all of that already
        succeeded and is left untouched. It exists so a partial-extraction
        failure can be repaired in place, without the cost of a full
        reingest and without minting a new document_id.

        If the stored document graph contains sections/elements but no final
        chunks, the workflow first re-runs post-classification chunk
        finalization in place (without embedding) and then continues with the
        extraction retry. If a saved extraction result already exists with
        unresolved chunk IDs, only that unresolved subset is retried and then
        merged back into the persisted result.

        See `ExtractionRetryStep.run` for the full implementation.
        """
        return self._pipeline.extraction_retry_step.run(
            document_id,
            activity_context=activity_context,
            progress_callback=progress_callback,
        )

    def _question_generation_model(self) -> str | None:
        question_service = getattr(
            self.post_classification_chunk_finalization_workflow,
            "question_generation_service",
            None,
        )
        return getattr(question_service, "question_generation_model", None)

    def _extraction_model(self) -> str | None:
        return getattr(self.extraction_workflow, "extraction_model", None)

    def _runtime_diagnostics(self) -> dict[str, object]:
        return self.runtime_capabilities.as_diagnostics()

    @staticmethod
    def _ensure_final_graph_has_chunks(
        *,
        final_graph,
        parsing_result,
    ) -> None:
        if final_graph.chunks:
            return
        raise IngestionWorkflowError(
            "Finalized ingestion graph contains no chunks for extraction and embedding.",
            error_code="ingestion.final_graph.no_chunks",
            details={
                "document_id": final_graph.document.document_id,
                "final_section_count": len(final_graph.sections),
                "final_element_count": len(final_graph.elements),
                "final_chunk_count": len(final_graph.chunks),
                "parsed_section_count": parsing_result.section_count,
                "parsed_element_count": parsing_result.element_count,
                "parsed_chunk_count": parsing_result.chunk_count,
            },
        )
