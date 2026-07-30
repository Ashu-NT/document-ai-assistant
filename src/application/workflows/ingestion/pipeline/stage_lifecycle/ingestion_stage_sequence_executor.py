from __future__ import annotations

import logging

from src.application.workflows.ingestion.models.ingestion_exceptions import (
    StaleParserVersionDetected,
)
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_result import IngestionResult
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.stage_lifecycle.sequence import (
    DocumentStructureStageSequence,
    SemanticIndexStageSequence,
)
from src.config.settings import ingestion_settings
from src.domain.common import DocumentType

logger = logging.getLogger(__name__)


def _coerce_document_type(value: str | None) -> DocumentType | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    for document_type in DocumentType:
        if normalized == document_type.value:
            return document_type
    return None


class IngestionStageSequenceExecutor:
    def __init__(
        self,
        *,
        stage_lifecycle,
        stage_payloads,
        stage_state_applier,
        duplicate_coordinator,
        parsing_stage_runner,
        registration_stage_runner,
        classification_stage_runner,
        finalization_stage_runner,
        extraction_stage_runner,
        vector_index_stage_runner,
        quality_check_step,
        success_finalizer,
        exception_handler,
        runtime_diagnostics_loader,
        ensure_final_graph_has_chunks,
        extraction_enabled: bool,
        extraction_model_loader,
    ) -> None:
        self.stage_lifecycle = stage_lifecycle
        self.stage_payloads = stage_payloads
        self.stage_state_applier = stage_state_applier
        self.duplicate_coordinator = duplicate_coordinator
        self.parsing_stage_runner = parsing_stage_runner
        self.success_finalizer = success_finalizer
        self.exception_handler = exception_handler
        self.extraction_enabled = extraction_enabled
        self.document_structure_sequence = DocumentStructureStageSequence(
            stage_lifecycle=stage_lifecycle,
            stage_payloads=stage_payloads,
            stage_state_applier=stage_state_applier,
            registration_stage_runner=registration_stage_runner,
            classification_stage_runner=classification_stage_runner,
            finalization_stage_runner=finalization_stage_runner,
            runtime_diagnostics_loader=runtime_diagnostics_loader,
            ensure_final_graph_has_chunks=ensure_final_graph_has_chunks,
            extraction_enabled=extraction_enabled,
            extraction_model_loader=extraction_model_loader,
        )
        self.semantic_index_sequence = SemanticIndexStageSequence(
            stage_lifecycle=stage_lifecycle,
            stage_payloads=stage_payloads,
            stage_state_applier=stage_state_applier,
            extraction_stage_runner=extraction_stage_runner,
            vector_index_stage_runner=vector_index_stage_runner,
            quality_check_step=quality_check_step,
            runtime_diagnostics_loader=runtime_diagnostics_loader,
            extraction_enabled=extraction_enabled,
        )
        self.runtime_diagnostics_loader = runtime_diagnostics_loader

    def run(
        self,
        *,
        request: IngestionRequest,
        file_path: str,
        file_name: str,
        file_hash: str,
        content_hash: str | None,
        correlation_id: str,
        ingestion_run,
        stage_session,
        activity_context,
        warnings: list[str],
    ) -> IngestionResult:
        parsing_result = None
        final_graph = None
        extraction_result = None
        embedded_chunks = []
        quality_diagnostics: dict[str, object] = {}
        current_stage = IngestionStage.PARSING

        try:
            parsing_result, content_hash = self._run_parsing(
                request=request,
                content_hash=content_hash,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
                warnings=warnings,
                file_path=file_path,
                file_name=file_name,
                file_hash=file_hash,
                correlation_id=correlation_id,
            )

            duplicate_result = self.duplicate_coordinator.check_content_hash_duplicate(
                request=request,
                ingestion_run=ingestion_run,
                duplicate_stage=IngestionStage.PARSING,
                file_name=file_name,
                file_path=file_path,
                file_hash=file_hash,
                content_hash=content_hash,
                correlation_id=correlation_id,
                warnings=warnings,
                activity_context=activity_context,
                event_context=stage_session.event_context,
                current_parser_version=parsing_result.document_graph.document.parser_version,
            )
            if duplicate_result is not None:
                return duplicate_result

            current_stage = IngestionStage.REGISTRATION
            self.document_structure_sequence.run_registration(
                request=request,
                parsing_result=parsing_result,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
            )

            current_stage = IngestionStage.CLASSIFICATION
            self.document_structure_sequence.run_classification(
                parsing_result=parsing_result,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
            )

            current_stage = IngestionStage.FINALIZATION
            final_graph = self.document_structure_sequence.run_finalization(
                request=request,
                parsing_result=parsing_result,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
            )

            current_stage = IngestionStage.EXTRACTION
            extraction_result = self.semantic_index_sequence.run_extraction(
                request=request,
                final_graph=final_graph,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
            )

            current_stage = IngestionStage.EMBEDDING
            embedded_chunks = self.semantic_index_sequence.run_embedding(
                final_graph=final_graph,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
                activity_context=activity_context,
            )

            current_stage = IngestionStage.INDEXING
            self.semantic_index_sequence.run_indexing(
                request=request,
                final_graph=final_graph,
                embedded_chunks=embedded_chunks,
                ingestion_run=ingestion_run,
                stage_session=stage_session,
            )

            if request.run_quality_checks:
                current_stage = IngestionStage.QUALITY
                quality_diagnostics = self.semantic_index_sequence.run_quality(
                    parsing_result=parsing_result,
                    final_graph=final_graph,
                    warnings=warnings,
                    stage_session=stage_session,
                )

            current_stage = IngestionStage.COMPLETE
            return self.success_finalizer.finalize(
                request=request,
                ingestion_run=ingestion_run,
                final_graph=final_graph,
                embedded_chunks=embedded_chunks,
                file_path=file_path,
                file_name=file_name,
                warnings=warnings,
                correlation_id=correlation_id,
                quality_diagnostics=quality_diagnostics,
                extraction_result=extraction_result,
                extraction_skipped=not self.extraction_enabled,
                runtime_diagnostics=self.runtime_diagnostics_loader(),
                event_context=stage_session.event_context,
                progress_callback=stage_session.progress_callback,
            )
        except StaleParserVersionDetected:
            # Not a failure - the ingestion_run was already finalized as
            # REDIRECTED_STALE_PARSER_VERSION by the duplicate coordinator.
            # Propagate so IngestionWorkflow.run() can redirect to reingest().
            raise
        except Exception as exc:
            self.exception_handler.handle(
                exc,
                ingestion_run=ingestion_run,
                current_stage=current_stage,
                file_path=file_path,
                file_name=file_name,
                event_context=stage_session.event_context,
                progress_callback=stage_session.progress_callback,
            )

    def _run_parsing(
        self,
        *,
        request: IngestionRequest,
        content_hash: str | None,
        ingestion_run,
        stage_session,
        activity_context,
        warnings: list[str],
        file_path: str,
        file_name: str,
        file_hash: str,
        correlation_id: str,
    ):
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.PARSING,
            status=IngestionStatus.PARSING,
        )
        parsing_stage_result = self.parsing_stage_runner.run(
            file_path=file_path,
            file_hash=file_hash,
            content_hash=content_hash,
            document_id=request.preserve_document_id,
            enable_ocr_override=request.enable_ocr,
            requested_title=request.title,
            requested_document_type=_coerce_document_type(request.document_type),
            source_name=request.source_name,
            activity_context=activity_context,
            progress_callback=stage_session.progress_callback,
        )
        parsing_result = parsing_stage_result.parsing_result
        next_content_hash = self.stage_state_applier.apply_parsing(
            ingestion_run,
            parsing_stage_result,
        )
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.PARSING,
            status=ingestion_run.status,
            payload=self.stage_payloads.parsing_completed(parsing_result),
        )
        parsing_stage_warnings = list(parsing_result.parse_warnings)
        if (
            parsing_result.parse_confidence is not None
            and parsing_result.parse_confidence
            < ingestion_settings.low_confidence_parse_threshold
        ):
            parsing_stage_warnings.append(
                f"Low parse confidence ({parsing_result.parse_confidence:.2f}); "
                "review this document's extraction quality before relying on it."
            )
        if parsing_stage_warnings:
            logger.warning(
                "parsing produced warnings",
                extra={
                    "document_id": parsing_result.document_id,
                    "correlation_id": correlation_id,
                    "parse_confidence": parsing_result.parse_confidence,
                    "warnings": parsing_stage_warnings,
                },
            )
        if parsing_result.stage_durations:
            logger.info(
                "parsing stage durations",
                extra={
                    "document_id": parsing_result.document_id,
                    "correlation_id": correlation_id,
                    "stage_durations": parsing_result.stage_durations,
                },
            )
        warnings.extend(parsing_stage_warnings)
        return parsing_result, next_content_hash
