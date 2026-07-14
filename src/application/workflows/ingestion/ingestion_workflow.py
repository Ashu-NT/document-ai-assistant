from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
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
from src.application.workflows.embedding import EmbeddedChunk, EmbeddingWorkflow
from src.application.workflows.extraction import ExtractionWorkflow
from src.application.workflows.ingestion.content_hash import compute_content_hash_from_graph
from src.application.workflows.ingestion.context.ingestion_execution_context_resolver import (
    resolve_activity_context,
    resolve_audit_context,
    resolve_event_context,
)
from src.application.workflows.ingestion.events.ingestion_stage_event_publisher import (
    IngestionStageEventPublisher,
)
from src.application.workflows.ingestion.hashing.file_hash_service import compute_file_hash
from src.application.workflows.linking import SemanticLinkingWorkflow
from src.application.workflows.ingestion.ingestion_exceptions import (
    IngestionWorkflowError,
)
from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.duplicate_check_step import (
    DuplicateCheckStep,
)
from src.application.workflows.ingestion.pipeline.extraction_retry_step import (
    ExtractionRetryStep,
)
from src.application.workflows.ingestion.pipeline.ingestion_result_assembler import (
    build_success_result,
)
from src.application.workflows.ingestion.pipeline.quality_check_step import (
    QualityCheckStep,
)
from src.application.workflows.ingestion.pipeline.reingestion_step import (
    ReingestionStep,
)
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
from src.shared.progress.progress_emitter import emit_progress
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
        extraction_enabled: bool = True,
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
        self.extraction_enabled = extraction_enabled
        self.quality_gate = quality_gate or DocumentQualityGate()
        self.identifier_promotion_service = identifier_promotion_service
        self.deterministic_identifier_scanner = deterministic_identifier_scanner
        self.document_lookup_service = document_lookup_service
        self.semantic_linking_workflow = semantic_linking_workflow
        self.activity_service = activity_service
        self.audit_service = audit_service
        self.event_service = event_service

        self._event_publisher = IngestionStageEventPublisher(
            id_generator=self.id_generator,
            event_service=self.event_service,
            unit_of_work=self.unit_of_work,
        )
        self._duplicate_check_step = DuplicateCheckStep(
            duplicate_detection_service=self.duplicate_detection_service,
        )
        self._quality_check_step = QualityCheckStep(quality_gate=self.quality_gate)
        self._reingestion_step = ReingestionStep(
            document_lookup_service=self.document_lookup_service,
        )
        self._extraction_retry_step = ExtractionRetryStep(
            document_lookup_service=self.document_lookup_service,
            post_classification_chunk_finalization_workflow=(
                self.post_classification_chunk_finalization_workflow
            ),
            extraction_workflow=self.extraction_workflow,
            document_registration_service=self.document_registration_service,
            id_generator=self.id_generator,
            unit_of_work=self.unit_of_work,
            extraction_enabled=self.extraction_enabled,
            identifier_promotion_service=self.identifier_promotion_service,
            deterministic_identifier_scanner=self.deterministic_identifier_scanner,
            semantic_linking_workflow=self.semantic_linking_workflow,
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

        file_path = str(Path(request.file_path).expanduser().resolve())
        file_name = _file_name_from_path(file_path)
        file_hash = compute_file_hash(Path(file_path))
        content_hash: str | None = None
        run_id = self.id_generator.new_id(IdPrefix.INGESTION_RUN)
        correlation_id = request.correlation_id or run_id
        resolved_activity_context = resolve_activity_context(
            request=request,
            correlation_id=correlation_id,
            activity_context=activity_context,
        )
        resolved_audit_context = resolve_audit_context(
            request=request,
            correlation_id=correlation_id,
            audit_context=audit_context,
        )
        resolved_event_context = resolve_event_context(
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
        self._event_publisher.publish_event(
            IngestionEvent.started(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=run_id,
                file_path=file_path,
                file_name=file_name,
            ),
            event_context=resolved_event_context,
        )

        warnings: list[str] = []

        emit_progress(progress_callback, f"Starting ingestion for {file_name}...")
        self._event_publisher.publish_stage_started(
            ingestion_run=ingestion_run,
            stage=IngestionStage.DUPLICATE_CHECK,
            event_context=resolved_event_context,
            file_name=file_name,
            progress_callback=progress_callback,
        )
        current_stage = IngestionStage.DUPLICATE_CHECK
        file_duplicate_document_id = self._duplicate_check_step.check_file_hash_duplicate(
            request=request,
            file_hash=file_hash,
            activity_context=resolved_activity_context,
        )
        if file_duplicate_document_id is not None:
            duplicate_status = IngestionStatus.SKIPPED_FILE_DUPLICATE
            ingestion_run.status = duplicate_status
            self._event_publisher.publish_stage_completed(
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
            self._event_publisher.publish_event(
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
        self._event_publisher.publish_stage_completed(
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
            self._event_publisher.publish_stage_started(
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
                document_id=request.preserve_document_id,
                enable_ocr_override=request.enable_ocr,
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
            self._event_publisher.publish_stage_completed(
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

            content_duplicate_document_id = (
                self._duplicate_check_step.check_content_hash_duplicate(
                    request=request,
                    content_hash=content_hash,
                    activity_context=resolved_activity_context,
                )
            )
            if content_duplicate_document_id is not None:
                duplicate_status = IngestionStatus.SKIPPED_CONTENT_DUPLICATE
                ingestion_run.status = duplicate_status
                ingestion_run.document_id = content_duplicate_document_id
                ingestion_run.finished_at = datetime.now(UTC)
                self._persist_run(ingestion_run)
                self._event_publisher.publish_event(
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
            self._event_publisher.publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.REGISTRATION,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            if request.preserve_document_id is not None:
                self.document_registration_service.replace_document_graph(
                    parsing_result.document_graph,
                    activity_context=resolved_activity_context,
                )
            else:
                self.document_registration_service.register_document_graph(
                    parsing_result.document_graph,
                    activity_context=resolved_activity_context,
                )
            self.unit_of_work.commit()
            self._set_run_status(
                ingestion_run,
                IngestionStatus.REGISTERED,
            )
            self._event_publisher.publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.REGISTRATION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=parsing_result.document_id,
                file_name=file_name,
                payload={"document_id": parsing_result.document_id},
            )

            current_stage = IngestionStage.CLASSIFICATION
            self._event_publisher.publish_stage_started(
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
            self._event_publisher.publish_stage_completed(
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
            self._event_publisher.publish_stage_started(
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
            ingestion_run.extraction_model = (
                self.extraction_workflow.extraction_model
                if self.extraction_enabled
                else None
            )
            self._set_run_status(
                ingestion_run,
                IngestionStatus.FINALIZED,
            )
            self._event_publisher.publish_stage_completed(
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
            self._event_publisher.publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EXTRACTION,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                progress_callback=(
                    progress_callback if self.extraction_enabled else None
                ),
            )
            semantic_relationships = None
            scanned_identifier_count = 0
            if self.extraction_enabled:
                extraction_result = self.extraction_workflow.extract(
                    final_graph.document.document_id,
                    list(final_graph.chunks.values()),
                    activity_context=resolved_activity_context,
                    progress_callback=progress_callback,
                    replace_existing=request.preserve_document_id is not None,
                    tables=final_graph.tables,
                    sections=final_graph.sections,
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
            else:
                skip_message = "Extraction skipped by config."
                if self.deterministic_identifier_scanner is not None:
                    skip_message = (
                        "Extraction skipped by config. Running deterministic "
                        "identifier scan only."
                    )
                emit_progress(progress_callback, skip_message)

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
                scanned_identifier_count = len(scanned_identifiers)
                if scanned_identifiers:
                    for identifier in scanned_identifiers:
                        final_graph.identifiers[identifier.identifier_id] = identifier
                    self.document_registration_service.register_document_identifiers(
                        scanned_identifiers,
                        activity_context=resolved_activity_context,
                    )
                    self.unit_of_work.commit()

            if self.semantic_linking_workflow is not None:
                semantic_relationships = self.semantic_linking_workflow.link(
                    final_graph.document.document_id
                )
                self.unit_of_work.commit()

            self._event_publisher.publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EXTRACTION,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={
                    "skipped": not self.extraction_enabled,
                    "reason": (
                        "disabled_by_config"
                        if not self.extraction_enabled
                        else None
                    ),
                    "extraction_id": (
                        extraction_result.extraction_id
                        if extraction_result is not None
                        else None
                    ),
                    "maintenance_task_count": (
                        len(extraction_result.maintenance_tasks)
                        if extraction_result is not None
                        else 0
                    ),
                    "spare_part_count": (
                        len(extraction_result.spare_parts)
                        if extraction_result is not None
                        else 0
                    ),
                    "unresolved_chunk_count": (
                        len(extraction_result.unresolved_chunk_ids)
                        if extraction_result is not None
                        else 0
                    ),
                    "deterministic_identifier_count": scanned_identifier_count,
                    "semantic_relationship_count": (
                        len(semantic_relationships)
                        if semantic_relationships is not None
                        else None
                    ),
                },
            )
            self._set_run_status(
                ingestion_run,
                IngestionStatus.EXTRACTED,
            )

            current_stage = IngestionStage.EMBEDDING
            self._event_publisher.publish_stage_started(
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
            self._event_publisher.publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.EMBEDDING,
                status=ingestion_run.status,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                payload={"vector_count": len(embedded_chunks)},
            )

            current_stage = IngestionStage.INDEXING
            self._event_publisher.publish_stage_started(
                ingestion_run=ingestion_run,
                stage=IngestionStage.INDEXING,
                event_context=resolved_event_context,
                document_id=final_graph.document.document_id,
                file_name=file_name,
                progress_callback=progress_callback,
            )
            if request.preserve_document_id is not None:
                self.embedding_workflow.delete_document_vectors(
                    final_graph.document.document_id
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
            self._event_publisher.publish_stage_completed(
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
                self._event_publisher.publish_stage_started(
                    ingestion_run=ingestion_run,
                    stage=IngestionStage.QUALITY,
                    event_context=resolved_event_context,
                    document_id=final_graph.document.document_id,
                    file_name=file_name,
                    progress_callback=progress_callback,
                )
                quality_diagnostics = self._quality_check_step.run(
                    parsing_result=parsing_result,
                    final_graph=final_graph,
                    warnings=warnings,
                )
                self._event_publisher.publish_stage_completed(
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
            result = build_success_result(
                request=request,
                ingestion_run=ingestion_run,
                final_graph=final_graph,
                embedded_chunks=embedded_chunks,
                file_name=file_name,
                warnings=warnings,
                correlation_id=correlation_id,
                quality_diagnostics=quality_diagnostics,
                extraction_result=extraction_result,
                extraction_skipped=not self.extraction_enabled,
            )
            self._event_publisher.publish_event(
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
            emit_progress(progress_callback, f"Ingestion completed for {file_name}.")
            return result

        except Exception as exc:
            self._rollback()
            ingestion_run.mark_status(
                IngestionStatus.FAILED,
                finished_at=datetime.now(UTC),
                error_message=str(exc),
            )
            self._persist_run(ingestion_run)
            self._event_publisher.publish_event(
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
            emit_progress(
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
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        ingestion_request = self._reingestion_step.prepare_request(
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
        return self._extraction_retry_step.run(
            document_id,
            activity_context=activity_context,
            progress_callback=progress_callback,
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
