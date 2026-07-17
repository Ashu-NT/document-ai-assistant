from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext

from .ingestion_run_store import IngestionRunStore


@dataclass(slots=True)
class IngestionStageSession:
    ingestion_run: IngestionRun
    file_name: str
    event_context: EventContext | None
    progress_callback: Callable[[str], None] | None


class IngestionStageLifecycleCoordinator:
    def __init__(self, *, run_store: IngestionRunStore, event_publisher) -> None:
        self.run_store = run_store
        self.event_publisher = event_publisher

    @staticmethod
    def create_session(
        *,
        ingestion_run: IngestionRun,
        file_name: str,
        event_context: EventContext | None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionStageSession:
        return IngestionStageSession(
            ingestion_run=ingestion_run,
            file_name=file_name,
            event_context=event_context,
            progress_callback=progress_callback,
        )

    def start(
        self,
        session: IngestionStageSession,
        *,
        stage: IngestionStage,
        status: IngestionStatus | None = None,
        document_id: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        if status is not None:
            self.run_store.mark_status(session.ingestion_run, status)
        self.event_publisher.publish_stage_started(
            ingestion_run=session.ingestion_run,
            stage=stage,
            event_context=session.event_context,
            document_id=document_id,
            file_name=session.file_name,
            progress_callback=progress_callback or session.progress_callback,
        )

    def complete(
        self,
        session: IngestionStageSession,
        *,
        stage: IngestionStage,
        payload: dict | None = None,
        document_id: str | None = None,
        status: IngestionStatus | None = None,
    ) -> None:
        self.event_publisher.publish_stage_completed(
            ingestion_run=session.ingestion_run,
            stage=stage,
            status=status or session.ingestion_run.status,
            event_context=session.event_context,
            document_id=document_id,
            file_name=session.file_name,
            payload=payload,
        )

    def mark_status(
        self,
        ingestion_run: IngestionRun,
        status: IngestionStatus,
    ) -> None:
        self.run_store.mark_status(ingestion_run, status)
