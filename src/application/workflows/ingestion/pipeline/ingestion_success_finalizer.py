from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable

from src.application.workflows.embedding import EmbeddedChunk
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_result import IngestionResult
from src.application.workflows.ingestion.pipeline.ingestion_result_assembler import (
    build_success_result,
)
from src.domain.document.aggregates.document_graph import DocumentGraph
from src.domain.events import IngestionEvent
from src.domain.extraction.extraction_result import ExtractionResult
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress

from .ingestion_run_store import IngestionRunStore


class IngestionSuccessFinalizer:
    def __init__(
        self,
        *,
        run_store: IngestionRunStore,
        id_generator: IdGenerator,
        event_publisher,
    ) -> None:
        self.run_store = run_store
        self.id_generator = id_generator
        self.event_publisher = event_publisher

    def finalize(
        self,
        *,
        request: IngestionRequest,
        ingestion_run: IngestionRun,
        final_graph: DocumentGraph,
        embedded_chunks: list[EmbeddedChunk],
        file_path: str,
        file_name: str,
        warnings: list[str],
        correlation_id: str,
        quality_diagnostics: dict[str, object],
        extraction_result: ExtractionResult | None,
        extraction_skipped: bool,
        runtime_diagnostics: dict[str, object],
        event_context: EventContext | None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult:
        ingestion_run.mark_complete(datetime.now(UTC))
        self.run_store.update(ingestion_run)
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
            extraction_skipped=extraction_skipped,
            runtime_diagnostics=runtime_diagnostics,
        )
        self.event_publisher.publish_event(
            IngestionEvent.completed(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                document_id=final_graph.document.document_id,
                file_path=file_path,
                file_name=file_name,
                payload={
                    "status": ingestion_run.status.value,
                    "chunk_count": result.chunk_count,
                    "vector_count": result.vector_count,
                },
            ),
            event_context=event_context,
        )
        emit_progress(progress_callback, f"Ingestion completed for {file_name}.")
        return result
