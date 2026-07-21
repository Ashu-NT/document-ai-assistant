from __future__ import annotations

from typing import Callable

from src.application.contracts import UnitOfWork
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.domain.events import IngestionEvent
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext
from src.shared.ids import IdGenerator
from src.shared.progress.progress_emitter import emit_progress


class IngestionStageEventPublisher:
    """Publishes ingestion-run stage-progress events (and their matching
    progress-callback messages) and commits the unit of work after every
    successful publish.
    """

    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        event_service,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.id_generator = id_generator
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def publish_stage_started(
        self,
        *,
        ingestion_run: IngestionRun,
        stage: IngestionStage,
        event_context: EventContext | None,
        file_name: str,
        progress_callback: Callable[[str], None] | None = None,
        document_id: str | None = None,
    ) -> None:
        emit_progress(progress_callback, f"{stage.value.replace('_', ' ').title()} started.")
        self.publish_event(
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

    def publish_stage_completed(
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
        self.publish_event(
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

    def publish_event(
        self,
        event: IngestionEvent,
        *,
        event_context: EventContext | None,
    ) -> None:
        if self.event_service is None:
            return
        self.event_service.publish(event, context=event_context)
        self.unit_of_work.commit()
