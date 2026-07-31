from __future__ import annotations

from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus


class DocumentStructureStageSequence:
    def __init__(
        self,
        *,
        stage_lifecycle,
        stage_payloads,
        stage_state_applier,
        registration_stage_runner,
        classification_stage_runner,
        finalization_stage_runner,
        runtime_diagnostics_loader,
        ensure_final_graph_has_chunks,
        extraction_enabled: bool,
        classification_enabled: bool,
        extraction_model_loader,
    ) -> None:
        self.stage_lifecycle = stage_lifecycle
        self.stage_payloads = stage_payloads
        self.stage_state_applier = stage_state_applier
        self.registration_stage_runner = registration_stage_runner
        self.classification_stage_runner = classification_stage_runner
        self.finalization_stage_runner = finalization_stage_runner
        self.runtime_diagnostics_loader = runtime_diagnostics_loader
        self.ensure_final_graph_has_chunks = ensure_final_graph_has_chunks
        self.extraction_enabled = extraction_enabled
        self.classification_enabled = classification_enabled
        self.extraction_model_loader = extraction_model_loader

    def run_registration(
        self,
        *,
        request,
        parsing_result,
        ingestion_run,
        stage_session,
        activity_context,
    ) -> None:
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.REGISTRATION,
            document_id=parsing_result.document_id,
        )
        self.registration_stage_runner.run(
            document_graph=parsing_result.document_graph,
            replace_existing=request.preserve_document_id is not None,
            activity_context=activity_context,
        )
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.REGISTERED)
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.REGISTRATION,
            document_id=parsing_result.document_id,
            payload=self.stage_payloads.registration_completed(
                parsing_result.document_id
            ),
        )

    def run_classification(
        self,
        *,
        parsing_result,
        ingestion_run,
        stage_session,
        activity_context,
    ):
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.CLASSIFICATION,
            document_id=parsing_result.document_id,
        )
        classification_stage_result = self.classification_stage_runner.run(
            document_graph=parsing_result.document_graph,
            activity_context=activity_context,
            progress_callback=stage_session.progress_callback,
        )
        classification = classification_stage_result.classification
        self.stage_state_applier.apply_classification(
            ingestion_run,
            classification_stage_result,
        )
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.CLASSIFIED)
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.CLASSIFICATION,
            document_id=(
                classification.document_id
                if classification is not None
                else parsing_result.document_id
            ),
            payload=self.stage_payloads.classification_completed(
                classification,
                classification_enabled=self.classification_enabled,
            ),
        )
        return classification

    def run_finalization(
        self,
        *,
        request,
        parsing_result,
        ingestion_run,
        stage_session,
        activity_context,
    ):
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.FINALIZATION,
            document_id=parsing_result.document_id,
        )
        finalization_stage_result = self.finalization_stage_runner.run(
            document_id=parsing_result.document_id,
            enable_question_generation=request.generate_questions,
            activity_context=activity_context,
            progress_callback=stage_session.progress_callback,
        )
        final_graph = finalization_stage_result.final_graph
        self.stage_state_applier.apply_finalization(
            ingestion_run,
            finalization_stage_result=finalization_stage_result,
            extraction_enabled=self.extraction_enabled,
            extraction_model=self.extraction_model_loader(),
        )
        self.ensure_final_graph_has_chunks(
            final_graph=final_graph,
            parsing_result=parsing_result,
        )
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.FINALIZED)
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.FINALIZATION,
            document_id=final_graph.document.document_id,
            payload=self.stage_payloads.finalization_completed(
                final_graph=final_graph,
                runtime_diagnostics=self.runtime_diagnostics_loader(),
            ),
        )
        return final_graph
