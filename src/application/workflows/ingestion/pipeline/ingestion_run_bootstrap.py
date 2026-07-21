from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.application.workflows.ingestion.context.ingestion_execution_context_resolver import (
    resolve_activity_context,
    resolve_audit_context,
    resolve_event_context,
)
from src.application.workflows.ingestion.hashing.file_hash_service import compute_file_hash
from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.ingestion_run_store import (
    IngestionRunStore,
)
from src.domain.events import IngestionEvent
from src.domain.workflow import IngestionRun
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.events import EventContext
from src.shared.ids import IdGenerator, IdPrefix
from src.shared.progress.progress_emitter import emit_progress


@dataclass(slots=True)
class IngestionRunBootstrapContext:
    request: IngestionRequest
    file_path: str
    file_name: str
    file_hash: str
    content_hash: str | None
    correlation_id: str
    ingestion_run: IngestionRun
    activity_context: ActivityContext | None
    audit_context: AuditContext | None
    event_context: EventContext | None
    warnings: list[str] = field(default_factory=list)


class IngestionRunBootstrapper:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        run_store: IngestionRunStore,
        event_publisher,
    ) -> None:
        self.id_generator = id_generator
        self.run_store = run_store
        self.event_publisher = event_publisher

    def bootstrap(
        self,
        request: IngestionRequest,
        *,
        activity_context: ActivityContext | None = None,
        audit_context: AuditContext | None = None,
        event_context: EventContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionRunBootstrapContext:
        file_path = str(Path(request.file_path).expanduser().resolve())
        file_name = Path(file_path).name or file_path
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
        self.run_store.create(ingestion_run)
        self.event_publisher.publish_event(
            IngestionEvent.started(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=run_id,
                file_path=file_path,
                file_name=file_name,
            ),
            event_context=resolved_event_context,
        )
        emit_progress(progress_callback, f"Starting ingestion for {file_name}...")
        return IngestionRunBootstrapContext(
            request=request,
            file_path=file_path,
            file_name=file_name,
            file_hash=file_hash,
            content_hash=content_hash,
            correlation_id=correlation_id,
            ingestion_run=ingestion_run,
            activity_context=resolved_activity_context,
            audit_context=resolved_audit_context,
            event_context=resolved_event_context,
        )
