from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.services.document import (
    DeterministicIdentifierScanner,
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
from src.application.workflows.embedding import EmbeddedChunk, EmbeddingWorkflow
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion.content_hash import compute_content_hash_from_graph
from src.application.workflows.ingestion.ingestion_exceptions import (
    IngestionWorkflowError,
    ReingestionNotSupportedError,
)
from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.reingestion_request import (
    ReingestionRequest,
)
from src.application.workflows.parsing import ParsingWorkflow
from src.domain.common import DocumentType
from src.domain.document.value_objects import DocumentHashes
from src.domain.events import IngestionEvent
from src.domain.workflow import IngestionRun
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.events import EventContext
from src.shared.exceptions import ApplicationError
from src.shared.execution import tracked_action
from src.shared.ids import IdGenerator, IdPrefix


def _file_name_from_path(file_path: str) -> str:
    return Path(file_path).name or file_path


def _coerce_document_type(value: str | None) -> DocumentType | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    for document_type in DocumentType:
        if normalized == document_type.value:
            return document_type
    return None


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
        quality_gate: DocumentQualityGate | None = None,
        identifier_promotion_service: IdentifierPromotionService | None = None,
        deterministic_identifier_scanner: DeterministicIdentifierScanner | None = None,
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
        self.quality_gate = quality_gate or DocumentQualityGate()
        self.identifier_promotion_service = identifier_promotion_service
        self.deterministic_identifier_scanner = deterministic_identifier_scanner
        self.activity_service = activity_service
        self.audit_service = audit_service
        self.event_service = event_service

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

        file_path = str(Path(request.file_path).expanduser().resolve())
        file_name = _file_name_from_path(file_path)
        file_hash = self._compute_file_hash(Path(file_path))
        content_hash: str | None = None
        run_id = self.id_generator.new_id(IdPrefix.INGESTION_RUN)
        correlation_id = request.correlation_id or run_id
        resolved_activity_context = self._resolve_activity_context(
            request=request,
            correlation_id=correlation_id,
            activity_context=activity_context,
        )
        resolved_audit_context = self._resolve_audit_context(
            request=request,
            correlation_id=correlation_id,
            audit_context=audit_context,
        )
        resolved_event_context = self._resolve_event_context(
            request=request,
            correlation_id=correlation_id,
            event_context=event_context,
        )

        ingestion_run = IngestionRun(
            run_id=run_id,
            file_path=file_path,
            file_hash=file_hash,
            content_hash=content_hash,
            status=IngestionStatus.PENDING,
        )
        self._persist_run(ingestion_run, create=True)
        self._publish_event(
            IngestionEvent.started(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=run_id,
                file_path=file_path,
                file_name=file_name,
            ),
            event_context=resolved_event_context,
        )

        warnings: list[str] = []

        self._emit_progress(progress_callback, f"Starting ingestion for {file_name}...")
        self._publish_stage_started(
            ingestion_run=ingestion_run,
            stage=IngestionStage.DUPLICATE_CHECK,
            event_context=resolved_event_context,
            file_name=file_name,
            progress_callback=progress_callback,
        )
        current_stage = IngestionStage.DUPLICATE_CHECK
        file_duplicate_document_id = self._check_file_hash_duplicate(
            request=request,
            file_hash=file_hash,
            activity_context=resolved_activity_context,
        )
        if file_duplicate_document_id is not None:
            duplicate_status = IngestionStatus.SKIPPED_FILE_DUPLICATE
            ingestion_run.status = duplicate_status
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.DUPLICATE_CHECK,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                file_name=file_name,
                payload={"duplicate": True, "type": "file_hash"},
            )
            ingestion_run.document_id = file_duplicate_document_id
            ingestion_run.finished_at = datetime.now(UTC)
            self._persist_run(ingestion_run)
            self._publish_event(
                IngestionEvent.skipped_duplicate(
                    event_id=self.id_generator.new_event_id(),
                    ingestion_run_id=run_id,
                    status=duplicate_status.value,
                    duplicate_of_document_id=file_duplicate_document_id,
                    duplicate_type="file_hash",
                    document_id=file_duplicate_document_id,
                    file_path=file_path,
                    file_name=file_name,
                ),
                event_context=resolved_event_context,
            )
            return IngestionResult(
                status=duplicate_status,
                ingestion_run_id=run_id,
                document_id=file_duplicate_document_id,
                file_name=file_name,
                duplicate_of_document_id=file_duplicate_document_id,
                warnings=warnings,
                diagnostics={
                    "file_path": file_path,
                    "file_hash": file_hash,
                    "content_hash": None,
                    "metadata": dict(request.metadata),
                },
                current_stage=IngestionStage.DUPLICATE_CHECK,
                correlation_id=correlation_id,
            )
        self._publish_stage_completed(
            ingestion_run=ingestion_run,
            stage=IngestionStage.DUPLICATE_CHECK,
            status=ingestion_run.status,
            event_context=resolved_event_context,
            file_name=file_name,
            payload={"duplicate": False},
        )

        parsing_result = None
        final_graph = None
        extraction_result = None
        embedded_chunks: list[EmbeddedChunk] = []
        quality_diagnostics: dict[str, object] = {}

        try:
            current_stage = IngestionStage.PARSING
            self._set_run_status(
                ingestion_run,
                IngestionStatus.PARSING,
            )
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.PARSING,
                event_context=resolved_event_context,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            parsing_result = self.parsing_workflow.parse(
                file_path=file_path,
                file_hash=file_hash,
                content_hash=content_hash,
                activity_context=resolved_activity_context,
                progress_callback=progress_callback,
            )
            if request.title:
                parsing_result.document_graph.document.title = request.title
            requested_document_type = _coerce_document_type(request.document_type)
            if requested_document_type is not None:
                parsing_result.document_graph.document.document_type = requested_document_type
            if request.source_name:
                parsing_result.document_graph.document.source_name = request.source_name
            ingestion_run.document_id = parsing_result.document_id
            parser = getattr(self.parsing_workflow, "parser", None)
            ingestion_run.parser_name = getattr(parser, "parser_name", None)
            ingestion_run.parser_version = getattr(parser, "parser_version", None)
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.PARSING,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                file_name=file_name,
                payload={
                    "page_count": parsing_result.page_count,
                    "section_count": parsing_result.section_count,
                    "chunk_count": parsing_result.chunk_count,
                },
            )
            warnings.extend(parsing_result.parse_warnings)
            content_hash = compute_content_hash_from_graph(parsing_result.document_graph)
            ingestion_run.content_hash = content_hash
            parsing_result.document_graph.document.hashes = DocumentHashes(
                file_hash=file_hash,
                content_hash=content_hash,
            )

            content_duplicate_document_id = self._check_content_hash_duplicate(
                request=request,
                content_hash=content_hash,
                activity_context=resolved_activity_context,
            )
            if content_duplicate_document_id is not None:
                duplicate_status = IngestionStatus.SKIPPED_CONTENT_DUPLICATE
                ingestion_run.status = duplicate_status
                ingestion_run.document_id = content_duplicate_document_id
                ingestion_run.finished_at = datetime.now(UTC)
                self._persist_run(ingestion_run)
                self._publish_event(
                    IngestionEvent.skipped_duplicate(
                        event_id=self.id_generator.new_event_id(),
                        ingestion_run_id=run_id,
                        status=duplicate_status.value,
                        duplicate_of_document_id=content_duplicate_document_id,
                        duplicate_type="content_hash",
                        document_id=content_duplicate_document_id,
                        file_path=file_path,
                        file_name=file_name,
                    ),
                    event_context=resolved_event_context,
                )
                return IngestionResult(
                    status=duplicate_status,
                    ingestion_run_id=run_id,
                    document_id=content_duplicate_document_id,
                    file_name=file_name,
                    duplicate_of_document_id=content_duplicate_document_id,
                    warnings=warnings,
                    diagnostics={
                        "file_path": file_path,
                        "file_hash": file_hash,
                        "content_hash": content_hash,
                        "metadata": dict(request.metadata),
                    },
                    current_stage=IngestionStage.PARSING,
                    correlation_id=correlation_id,
                )

            current_stage = IngestionStage.REGISTRATION
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.REGISTRATION,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            self.document_registration_service.register_document_graph(
                parsing_result.document_graph,
                activity_context=resolved_activity_context,
            )
            self.unit_of_work.commit()
            self._set_run_status(
                ingestion_run,
                IngestionStatus.REGISTERED,
            )
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.REGISTRATION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                payload={"document_id": parsing_result.document_id},
            )

            current_stage = IngestionStage.CLASSIFICATION
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.CLASSIFICATION,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            classification = self.document_classification_workflow.classify_document(
                parsing_result.document_graph,
                activity_context=resolved_activity_context,
            )
            self.unit_of_work.commit()
            ingestion_run.classification_model = (
                classification.result.processing_metadata.model_name
                if classification.result is not None
                else None
            )
            self._set_run_status(
                ingestion_run,
                IngestionStatus.CLASSIFIED,
            )
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.CLASSIFICATION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=classification.document_id,
                file_name=file_name,
                payload={
                    "document_type": classification.document_type.value,
                    "confidence_score": (
                        classification.result.confidence_score
                        if classification.result is not None
                        else None
                    ),
                },
            )

            current_stage = IngestionStage.FINALIZATION
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.FINALIZATION,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            final_graph = self.post_classification_chunk_finalization_workflow.finalize(
                parsing_result.document_id,
                activity_context=resolved_activity_context,
                progress_callback=progress_callback,
                embed_final_chunks=False,
                enable_question_generation=request.generate_questions,
            )
            self.unit_of_work.commit()
            ingestion_run.question_generation_model = self._question_generation_model()
            ingestion_run.extraction_model = self.extraction_workflow.extraction_model
            self._set_run_status(
                ingestion_run,
                IngestionStatus.FINALIZED,
            )
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.FINALIZATION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={
                    "chunk_count": len(final_graph.chunks),
                    "question_count": len(final_graph.questions),
                },
            )

            if not final_graph.chunks:
                raise IngestionWorkflowError(
                    "Finalized ingestion graph contains no chunks for extraction and embedding.",
                    error_code="ingestion.final_graph.no_chunks",
                    details={"document_id": final_graph.document.document_id},
                )

            current_stage = IngestionStage.EXTRACTION
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EXTRACTION,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            extraction_result = self.extraction_workflow.extract(
                final_graph.document.document_id,
                list(final_graph.chunks.values()),
                activity_context=resolved_activity_context,
                progress_callback=progress_callback,
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
                        activity_context=resolved_activity_context,
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
                        activity_context=resolved_activity_context,
                    )
                    self.unit_of_work.commit()
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EXTRACTION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={
                    "extraction_id": extraction_result.extraction_id,
                    "maintenance_task_count": len(extraction_result.maintenance_tasks),
                    "spare_part_count": len(extraction_result.spare_parts),
                },
            )
            self._set_run_status(
                ingestion_run,
                IngestionStatus.EXTRACTED,
            )

            current_stage = IngestionStage.EMBEDDING
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EMBEDDING,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            embedded_chunks = self.embedding_workflow.embed_chunks(
                list(final_graph.chunks.values()),
                activity_context=resolved_activity_context,
                progress_callback=progress_callback,
            )
            ingestion_run.embedding_model = self.embedding_workflow.embedding_service.model_name
            self._set_run_status(
                ingestion_run,
                IngestionStatus.EMBEDDED,
            )
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EMBEDDING,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={"vector_count": len(embedded_chunks)},
            )

            current_stage = IngestionStage.INDEXING
            self._publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.INDEXING,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            self.embedding_workflow.store_embedded_chunks(
                embedded_chunks,
                progress_callback=progress_callback,
            )
            self.unit_of_work.commit()
            self._set_run_status(
                ingestion_run,
                IngestionStatus.INDEXED,
            )
            self._publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.INDEXING,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={"vector_count": len(embedded_chunks)},
            )

            if request.run_quality_checks:
                current_stage = IngestionStage.QUALITY
                self._publish_stage_started(
                    ingestion_run=ingestion_run,
                    stage=IngestionStage.QUALITY,
                    event_context=resolved_event_context,
                    document_id=final_graph.document.document_id,
                    file_name=file_name,
                    progress_callback=progress_callback,
                )
                quality_diagnostics = self._run_quality_checks(
                    parsing_result=parsing_result,
                    final_graph=final_graph,
                    warnings=warnings,
                )
                self._publish_stage_completed(
                    ingestion_run=ingestion_run,
                    stage=IngestionStage.QUALITY,
                    status=ingestion_run.status,
                    event_context=resolved_event_context,
                    document_id=final_graph.document.document_id,
                    file_name=file_name,
                    payload=quality_diagnostics,
                )

            current_stage = IngestionStage.COMPLETE
            ingestion_run.mark_complete(datetime.now(UTC))
            self._persist_run(ingestion_run)
            result = self._build_success_result(
                request=request,
                ingestion_run=ingestion_run,
                final_graph=final_graph,
                embedded_chunks=embedded_chunks,
                file_name=file_name,
                warnings=warnings,
                correlation_id=correlation_id,
                quality_diagnostics=quality_diagnostics,
                extraction_result=extraction_result.extraction_id if extraction_result else None,
            )
            self._publish_event(
                IngestionEvent.completed(
                    event_id=self.id_generator.new_event_id(),
                    ingestion_run_id=run_id,
                    document_id=final_graph.document.document_id,
                    file_path=file_path,
                    file_name=file_name,
                    payload={
                        "status": ingestion_run.status.value,
                        "chunk_count": result.chunk_count,
                        "vector_count": result.vector_count,
                    },
                ),
                event_context=resolved_event_context,
            )
            self._emit_progress(progress_callback, f"Ingestion completed for {file_name}.")
            return result

        except Exception as exc:
            self._rollback()
            ingestion_run.mark_status(
                IngestionStatus.FAILED,
                finished_at=datetime.now(UTC),
                error_message=str(exc),
            )
            self._persist_run(ingestion_run)
            self._publish_event(
                IngestionEvent.failed(
                    event_id=self.id_generator.new_event_id(),
                    ingestion_run_id=run_id,
                    error_message=str(exc),
                    document_id=ingestion_run.document_id,
                    stage=current_stage.value if current_stage is not None else None,
                    file_path=file_path,
                    file_name=file_name,
                    details={"error_code": getattr(exc, "error_code", None)},
                ),
                event_context=resolved_event_context,
            )
            self._emit_progress(
                progress_callback,
                f"Ingestion failed for {file_name}: {exc}",
            )
            if isinstance(exc, ApplicationError):
                raise
            raise IngestionWorkflowError(
                "Document ingestion failed unexpectedly.",
                error_code="ingestion.workflow.failed",
                details={
                    "document_id": ingestion_run.document_id,
                    "file_path": file_path,
                    "run_id": run_id,
                },
            ) from exc

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
    ) -> IngestionResult:
        raise ReingestionNotSupportedError(
            "Reingestion is not implemented safely yet because extraction results are not replaced atomically for an existing document.",
            error_code="reingestion_not_supported",
            details={"document_id": request.document_id},
        )

    def _check_file_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        file_hash: str,
        activity_context,
    ) -> str | None:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return None

        if not duplicate_detection_settings.enable_file_hash_check:
            return None

        result = self.duplicate_detection_service.check_file_hash(
            file_hash,
            activity_context=activity_context,
        )
        return result.payload.get("existing_document_id")

    def _check_content_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        content_hash: str,
        activity_context,
    ) -> str | None:
        from src.config.settings import duplicate_detection_settings

        if request.force:
            return None

        if not duplicate_detection_settings.enable_content_hash_check:
            return None

        result = self.duplicate_detection_service.check_content_hash(
            content_hash,
            activity_context=activity_context,
        )
        return result.payload.get("existing_document_id")

    def _run_quality_checks(
        self,
        *,
        parsing_result,
        final_graph,
        warnings: list[str],
    ) -> dict[str, object]:
        parsing_quality = self.quality_gate.check_parsing(
            final_graph.document.document_id,
            sections=list(final_graph.sections.values()),
            elements=list(final_graph.elements.values()),
            ocr_trace=parsing_result.ocr_trace,
        )
        chunking_quality = self.quality_gate.check_chunking(
            final_graph.document.document_id,
            chunks=list(final_graph.chunks.values()),
        )
        for quality_result in (parsing_quality, chunking_quality):
            for check in quality_result.failures():
                warnings.append(f"{check.check_name}: {check.message}")
        return {
            "parsing_quality": parsing_quality.summary(),
            "chunking_quality": chunking_quality.summary(),
        }

    def _build_success_result(
        self,
        *,
        request: IngestionRequest,
        ingestion_run: IngestionRun,
        final_graph,
        embedded_chunks: list[EmbeddedChunk],
        file_name: str,
        warnings: list[str],
        correlation_id: str,
        quality_diagnostics: dict[str, object],
        extraction_result: str | None,
    ) -> IngestionResult:
        statistics = final_graph.document.statistics
        diagnostics = {
            "file_path": final_graph.document.file_path,
            "file_hash": final_graph.document.hashes.file_hash,
            "content_hash": final_graph.document.hashes.content_hash,
            "metadata": dict(request.metadata),
            "quality": quality_diagnostics,
            "vector_indexing_boundary": (
                "Qdrant writes and SQLite vector mappings are orchestrated in order but are not atomic across both stores."
            ),
        }
        if request.source_name:
            diagnostics["source_name"] = request.source_name
        if extraction_result is not None:
            diagnostics["extraction_id"] = extraction_result

        return IngestionResult(
            status=IngestionStatus.COMPLETE,
            ingestion_run_id=ingestion_run.run_id,
            document_id=final_graph.document.document_id,
            title=final_graph.document.title,
            file_name=file_name,
            document_type=final_graph.document.document_type.value,
            page_count=statistics.page_count,
            section_count=statistics.section_count,
            element_count=statistics.element_count,
            chunk_count=statistics.chunk_count,
            table_count=statistics.table_count,
            picture_count=statistics.picture_count,
            identifier_count=statistics.identifier_count,
            generated_question_count=len(final_graph.questions),
            vector_count=len(embedded_chunks),
            warnings=warnings,
            diagnostics=diagnostics,
            current_stage=IngestionStage.COMPLETE,
            correlation_id=correlation_id,
        )

    def _persist_run(self, ingestion_run: IngestionRun, *, create: bool = False) -> None:
        if create:
            self.unit_of_work.ingestion_runs.create(ingestion_run)
        else:
            self.unit_of_work.ingestion_runs.update(ingestion_run)
        self.unit_of_work.commit()

    def _set_run_status(
        self,
        ingestion_run: IngestionRun,
        status: IngestionStatus,
    ) -> None:
        ingestion_run.mark_status(status, error_message=None)
        self._persist_run(ingestion_run)

    def _publish_stage_started(
        self,
        *,
        ingestion_run: IngestionRun,
        stage: IngestionStage,
        event_context: EventContext | None,
        file_name: str,
        progress_callback: Callable[[str], None] | None = None,
        document_id: str | None = None,
    ) -> None:
        self._emit_progress(progress_callback, f"{stage.value.replace('_', ' ').title()} started.")
        self._publish_event(
            IngestionEvent.stage_started(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                stage=stage.value,
                document_id=document_id or ingestion_run.document_id,
                file_path=ingestion_run.file_path,
                file_name=file_name,
            ),
            event_context=event_context,
        )

    def _publish_stage_completed(
        self,
        *,
        ingestion_run: IngestionRun,
        stage: IngestionStage,
        status: IngestionStatus,
        event_context: EventContext | None,
        file_name: str,
        payload: dict | None = None,
        document_id: str | None = None,
    ) -> None:
        self._publish_event(
            IngestionEvent.stage_completed(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                stage=stage.value,
                status=status.value,
                document_id=document_id or ingestion_run.document_id,
                file_path=ingestion_run.file_path,
                file_name=file_name,
                payload=payload,
            ),
            event_context=event_context,
        )

    def _publish_event(
        self,
        event: IngestionEvent,
        *,
        event_context: EventContext | None,
    ) -> None:
        if self.event_service is None:
            return
        self.event_service.publish(event, context=event_context)
        self.unit_of_work.commit()

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _resolve_activity_context(
        self,
        *,
        request: IngestionRequest,
        correlation_id: str,
        activity_context: ActivityContext | None,
    ) -> ActivityContext:
        if activity_context is not None:
            return activity_context
        return ActivityContext(
            actor_id=request.requested_by,
            actor_type="user" if request.requested_by else "system",
            request_id=correlation_id,
            correlation_id=correlation_id,
            source="ingestion_workflow",
        )

    def _resolve_audit_context(
        self,
        *,
        request: IngestionRequest,
        correlation_id: str,
        audit_context: AuditContext | None,
    ) -> AuditContext:
        if audit_context is not None:
            return audit_context
        return AuditContext(
            actor_id=request.requested_by,
            actor_type="user" if request.requested_by else "system",
            request_id=correlation_id,
            correlation_id=correlation_id,
            source="ingestion_workflow",
        )

    def _resolve_event_context(
        self,
        *,
        request: IngestionRequest,
        correlation_id: str,
        event_context: EventContext | None,
    ) -> EventContext:
        if event_context is not None:
            return event_context
        return EventContext(
            actor_id=request.requested_by,
            actor_type="user" if request.requested_by else "system",
            request_id=correlation_id,
            correlation_id=correlation_id,
            source="ingestion_workflow",
        )

    def _question_generation_model(self) -> str | None:
        question_service = getattr(
            self.post_classification_chunk_finalization_workflow,
            "question_generation_service",
            None,
        )
        return getattr(question_service, "question_generation_model", None)

    def _rollback(self) -> None:
        try:
            self.unit_of_work.rollback()
        except Exception:
            return
