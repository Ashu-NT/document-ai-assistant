from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable, NoReturn

from src.application.workflows.ingestion.models.ingestion_exceptions import (
    IngestionWorkflowError,
)
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.run.ingestion_run_store import (
    IngestionRunStore,
)
from src.domain.events import IngestionEvent
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext
from src.shared.exceptions import ApplicationError, DatabaseError
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress


class IngestionExceptionHandler:
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

    def handle(
        self,
        exc: Exception,
        *,
        ingestion_run: IngestionRun,
        current_stage: IngestionStage | None,
        file_path: str,
        file_name: str,
        event_context: EventContext | None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> NoReturn:
        self.run_store.rollback()
        original_document_id = ingestion_run.document_id
        ingestion_run.mark_status(
            IngestionStatus.FAILED,
            finished_at=datetime.now(UTC),
            error_message=str(exc),
        )
        try:
            self.run_store.update(ingestion_run)
        except DatabaseError:
            ingestion_run.document_id = None
            self.run_store.update(ingestion_run)
        self.event_publisher.publish_event(
            IngestionEvent.failed(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                error_message=str(exc),
                document_id=original_document_id,
                stage=current_stage.value if current_stage is not None else None,
                file_path=file_path,
                file_name=file_name,
                details={"error_code": getattr(exc, "error_code", None)},
            ),
            event_context=event_context,
        )
        emit_progress(progress_callback, f"Ingestion failed for {file_name}: {exc}")
        if isinstance(exc, ApplicationError):
            raise exc
        raise IngestionWorkflowError(
            "Document ingestion failed unexpectedly.",
            error_code="ingestion.workflow.failed",
            details={
                "document_id": ingestion_run.document_id,
                "file_path": file_path,
                "run_id": ingestion_run.run_id,
            },
        ) from exc
