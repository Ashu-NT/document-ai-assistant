from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.config.logging import get_logger
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext
from src.shared.observability.stage_logger import log_stage_result

from src.application.workflows.ingestion.pipeline.run.ingestion_run_store import (
    IngestionRunStore,
)

_logger = get_logger(__name__)


def _loggable_payload(payload: dict | None) -> dict:
    """Keep only primitive summary values from a stage payload for logging
    - payloads built by stage_payloads.*_completed(...) often carry nested
    domain objects (a full classification/extraction result) that would
    make the log line huge and unreadable; the primitive counts they also
    carry (e.g. chunk_count, confidence) are what's useful here."""
    if not payload:
        return {}
    return {
        key: value
        for key, value in payload.items()
        if value is None or isinstance(value, (int, float, str, bool))
    }


@dataclass(slots=True)
class IngestionStageSession:
    ingestion_run: IngestionRun
    file_name: str
    event_context: EventContext | None
    progress_callback: Callable[[str], None] | None
    stage_started_at: dict[IngestionStage, float] = field(default_factory=dict)


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
        session.stage_started_at[stage] = time.perf_counter()
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
        started_at = session.stage_started_at.pop(stage, None)
        if started_at is not None:
            log_stage_result(
                _logger,
                stage_name=stage.value,
                duration_ms=(time.perf_counter() - started_at) * 1000,
                status="ok",
                document_id=document_id or session.ingestion_run.document_id,
                ingestion_run_id=session.ingestion_run.run_id,
                counts=_loggable_payload(payload),
            )
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
