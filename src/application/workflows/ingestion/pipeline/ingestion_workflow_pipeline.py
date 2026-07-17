from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.ingestion.events.ingestion_stage_event_publisher import (
    IngestionStageEventPublisher,
)
from src.application.workflows.ingestion.pipeline.duplicate_check_step import (
    DuplicateCheckStep,
)
from src.application.workflows.ingestion.pipeline.duplicate_ingestion_exit_handler import (
    DuplicateIngestionExitHandler,
)
from src.application.workflows.ingestion.pipeline.extraction_retry_step import (
    ExtractionRetryStep,
)
from src.application.workflows.ingestion.pipeline.ingestion_duplicate_coordinator import (
    IngestionDuplicateCoordinator,
)
from src.application.workflows.ingestion.pipeline.ingestion_exception_handler import (
    IngestionExceptionHandler,
)
from src.application.workflows.ingestion.pipeline.ingestion_run_bootstrap import (
    IngestionRunBootstrapper,
)
from src.application.workflows.ingestion.pipeline.ingestion_run_store import (
    IngestionRunStore,
)
from src.application.workflows.ingestion.pipeline.ingestion_stage_lifecycle_coordinator import (
    IngestionStageLifecycleCoordinator,
)
from src.application.workflows.ingestion.pipeline.ingestion_stage_payload_builder import (
    IngestionStagePayloadBuilder,
)
from src.application.workflows.ingestion.pipeline.ingestion_stage_sequence_executor import (
    IngestionStageSequenceExecutor,
)
from src.application.workflows.ingestion.pipeline.ingestion_stage_state_applier import (
    IngestionStageStateApplier,
)
from src.application.workflows.ingestion.pipeline.ingestion_success_finalizer import (
    IngestionSuccessFinalizer,
)
from src.application.workflows.ingestion.pipeline.quality_check_step import (
    QualityCheckStep,
)
from src.application.workflows.ingestion.pipeline.reingestion_step import (
    ReingestionStep,
)
from src.application.workflows.ingestion.stages import (
    ClassificationStageRunner,
    ExtractionStageRunner,
    FinalizationStageRunner,
    ParsingStageRunner,
    RegistrationStageRunner,
    VectorIndexStageRunner,
)


@dataclass(slots=True)
class IngestionWorkflowPipeline:
    run_bootstrapper: IngestionRunBootstrapper
    stage_lifecycle: IngestionStageLifecycleCoordinator
    duplicate_coordinator: IngestionDuplicateCoordinator
    stage_sequence_executor: IngestionStageSequenceExecutor
    reingestion_step: ReingestionStep
    extraction_retry_step: ExtractionRetryStep


def build_ingestion_workflow_pipeline(
    *,
    unit_of_work,
    id_generator,
    event_service,
    duplicate_detection_service,
    quality_gate,
    document_lookup_service,
    post_classification_chunk_finalization_workflow,
    extraction_workflow,
    document_registration_service,
    identifier_promotion_service,
    deterministic_identifier_scanner,
    semantic_linking_workflow,
    parsing_workflow,
    document_classification_workflow,
    embedding_workflow,
    runtime_capabilities,
    extraction_enabled: bool,
    runtime_diagnostics_loader,
    question_generation_model_loader,
    extraction_model_loader,
    ensure_final_graph_has_chunks,
) -> IngestionWorkflowPipeline:
    run_store = IngestionRunStore(unit_of_work=unit_of_work)
    event_publisher = IngestionStageEventPublisher(
        id_generator=id_generator,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )
    run_bootstrapper = IngestionRunBootstrapper(
        id_generator=id_generator,
        run_store=run_store,
        event_publisher=event_publisher,
    )
    duplicate_exit_handler = DuplicateIngestionExitHandler(
        run_store=run_store,
        id_generator=id_generator,
        event_publisher=event_publisher,
        runtime_diagnostics_loader=runtime_diagnostics_loader,
    )
    exception_handler = IngestionExceptionHandler(
        run_store=run_store,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )
    success_finalizer = IngestionSuccessFinalizer(
        run_store=run_store,
        id_generator=id_generator,
        event_publisher=event_publisher,
    )
    stage_lifecycle = IngestionStageLifecycleCoordinator(
        run_store=run_store,
        event_publisher=event_publisher,
    )
    stage_payloads = IngestionStagePayloadBuilder()
    stage_state_applier = IngestionStageStateApplier()
    duplicate_check_step = DuplicateCheckStep(
        duplicate_detection_service=duplicate_detection_service,
    )
    duplicate_coordinator = IngestionDuplicateCoordinator(
        duplicate_check_step=duplicate_check_step,
        duplicate_exit_handler=duplicate_exit_handler,
        event_publisher=event_publisher,
    )
    quality_check_step = QualityCheckStep(quality_gate=quality_gate)
    reingestion_step = ReingestionStep(
        document_lookup_service=document_lookup_service,
    )
    extraction_retry_step = ExtractionRetryStep(
        document_lookup_service=document_lookup_service,
        post_classification_chunk_finalization_workflow=(
            post_classification_chunk_finalization_workflow
        ),
        extraction_workflow=extraction_workflow,
        document_registration_service=document_registration_service,
        id_generator=id_generator,
        unit_of_work=unit_of_work,
        runtime_capabilities=runtime_capabilities,
        identifier_promotion_service=identifier_promotion_service,
        deterministic_identifier_scanner=deterministic_identifier_scanner,
        semantic_linking_workflow=semantic_linking_workflow,
    )
    stage_sequence_executor = IngestionStageSequenceExecutor(
        stage_lifecycle=stage_lifecycle,
        stage_payloads=stage_payloads,
        stage_state_applier=stage_state_applier,
        duplicate_coordinator=duplicate_coordinator,
        parsing_stage_runner=ParsingStageRunner(parsing_workflow=parsing_workflow),
        registration_stage_runner=RegistrationStageRunner(
            document_registration_service=document_registration_service,
            commit=unit_of_work.commit,
        ),
        classification_stage_runner=ClassificationStageRunner(
            document_classification_workflow=document_classification_workflow,
            commit=unit_of_work.commit,
        ),
        finalization_stage_runner=FinalizationStageRunner(
            post_classification_chunk_finalization_workflow=(
                post_classification_chunk_finalization_workflow
            ),
            question_generation_model_loader=question_generation_model_loader,
            commit=unit_of_work.commit,
        ),
        extraction_stage_runner=ExtractionStageRunner(
            extraction_workflow=extraction_workflow,
            document_registration_service=document_registration_service,
            id_generator=id_generator,
            extraction_enabled=extraction_enabled,
            commit=unit_of_work.commit,
            identifier_promotion_service=identifier_promotion_service,
            deterministic_identifier_scanner=deterministic_identifier_scanner,
            semantic_linking_workflow=semantic_linking_workflow,
        ),
        vector_index_stage_runner=VectorIndexStageRunner(
            embedding_workflow=embedding_workflow,
            commit=unit_of_work.commit,
        ),
        quality_check_step=quality_check_step,
        success_finalizer=success_finalizer,
        exception_handler=exception_handler,
        runtime_diagnostics_loader=runtime_diagnostics_loader,
        ensure_final_graph_has_chunks=ensure_final_graph_has_chunks,
        extraction_enabled=extraction_enabled,
        extraction_model_loader=extraction_model_loader,
    )
    return IngestionWorkflowPipeline(
        run_bootstrapper=run_bootstrapper,
        stage_lifecycle=stage_lifecycle,
        duplicate_coordinator=duplicate_coordinator,
        stage_sequence_executor=stage_sequence_executor,
        reingestion_step=reingestion_step,
        extraction_retry_step=extraction_retry_step,
    )
