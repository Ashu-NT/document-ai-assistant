from __future__ import annotations

from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus


class SemanticIndexStageSequence:
    def __init__(
        self,
        *,
        stage_lifecycle,
        stage_payloads,
        stage_state_applier,
        extraction_stage_runner,
        vector_index_stage_runner,
        quality_check_step,
        runtime_diagnostics_loader,
        extraction_enabled: bool,
    ) -> None:
        self.stage_lifecycle = stage_lifecycle
        self.stage_payloads = stage_payloads
        self.stage_state_applier = stage_state_applier
        self.extraction_stage_runner = extraction_stage_runner
        self.vector_index_stage_runner = vector_index_stage_runner
        self.quality_check_step = quality_check_step
        self.runtime_diagnostics_loader = runtime_diagnostics_loader
        self.extraction_enabled = extraction_enabled

    def run_extraction(
        self,
        *,
        request,
        final_graph,
        ingestion_run,
        stage_session,
        activity_context,
    ):
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.EXTRACTION,
            document_id=final_graph.document.document_id,
            progress_callback=(
                stage_session.progress_callback if self.extraction_enabled else None
            ),
        )
        extraction_stage_result = self.extraction_stage_runner.run(
            final_graph=final_graph,
            replace_existing=request.preserve_document_id is not None,
            activity_context=activity_context,
            progress_callback=stage_session.progress_callback,
        )
        extraction_result = extraction_stage_result.extraction_result
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.EXTRACTION,
            document_id=final_graph.document.document_id,
            payload=self.stage_payloads.extraction_completed(
                extraction_result=extraction_result,
                extraction_stage_result=extraction_stage_result,
                extraction_enabled=self.extraction_enabled,
                runtime_diagnostics=self.runtime_diagnostics_loader(),
            ),
        )
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.EXTRACTED)
        return extraction_result

    def run_embedding(
        self,
        *,
        final_graph,
        ingestion_run,
        stage_session,
        activity_context,
    ):
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.EMBEDDING,
            document_id=final_graph.document.document_id,
        )
        vector_stage_result = self.vector_index_stage_runner.embed(
            final_graph=final_graph,
            activity_context=activity_context,
            progress_callback=stage_session.progress_callback,
        )
        embedded_chunks = vector_stage_result.embedded_chunks
        self.stage_state_applier.apply_embedding(ingestion_run, vector_stage_result)
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.EMBEDDED)
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.EMBEDDING,
            document_id=final_graph.document.document_id,
            payload=self.stage_payloads.vector_completed(len(embedded_chunks)),
        )
        return embedded_chunks

    def run_indexing(
        self,
        *,
        request,
        final_graph,
        embedded_chunks,
        ingestion_run,
        stage_session,
    ) -> None:
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.INDEXING,
            document_id=final_graph.document.document_id,
        )
        self.vector_index_stage_runner.index(
            document_id=final_graph.document.document_id,
            embedded_chunks=embedded_chunks,
            replace_existing=request.preserve_document_id is not None,
            progress_callback=stage_session.progress_callback,
        )
        self.stage_lifecycle.mark_status(ingestion_run, IngestionStatus.INDEXED)
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.INDEXING,
            document_id=final_graph.document.document_id,
            payload=self.stage_payloads.vector_completed(len(embedded_chunks)),
        )

    def run_quality(
        self,
        *,
        parsing_result,
        final_graph,
        warnings: list[str],
        stage_session,
    ) -> dict[str, object]:
        self.stage_lifecycle.start(
            stage_session,
            stage=IngestionStage.QUALITY,
            document_id=final_graph.document.document_id,
        )
        quality_diagnostics = self.quality_check_step.run(
            parsing_result=parsing_result,
            final_graph=final_graph,
            warnings=warnings,
        )
        self.stage_lifecycle.complete(
            stage_session,
            stage=IngestionStage.QUALITY,
            document_id=final_graph.document.document_id,
            payload=quality_diagnostics,
        )
        return quality_diagnostics
