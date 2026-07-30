from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable

from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.models.ingestion_result import IngestionResult
from src.application.workflows.ingestion.models.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.models.ingestion_status import IngestionStatus
from src.application.workflows.ingestion.pipeline.run.ingestion_run_store import (
    IngestionRunStore,
)
from src.domain.events import IngestionEvent
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext
from src.shared.ids import IdGenerator


class DuplicateIngestionExitHandler:
    def __init__(
        self,
        *,
        run_store: IngestionRunStore,
        id_generator: IdGenerator,
        event_publisher,
        runtime_diagnostics_loader: Callable[[], dict[str, object]],
    ) -> None:
        self.run_store = run_store
        self.id_generator = id_generator
        self.event_publisher = event_publisher
        self.runtime_diagnostics_loader = runtime_diagnostics_loader

    def handle(
        self,
        *,
        request: IngestionRequest,
        ingestion_run: IngestionRun,
        duplicate_document_id: str,
        duplicate_type: str,
        current_stage: IngestionStage,
        file_name: str,
        file_path: str,
        file_hash: str,
        content_hash: str | None,
        correlation_id: str,
        warnings: list[str],
        event_context: EventContext | None,
    ) -> IngestionResult:
        duplicate_status = self._status_for_duplicate_type(duplicate_type)
        ingestion_run.status = duplicate_status
        ingestion_run.document_id = duplicate_document_id
        ingestion_run.finished_at = datetime.now(UTC)
        self.run_store.update(ingestion_run)
        self.event_publisher.publish_event(
            IngestionEvent.skipped_duplicate(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                status=duplicate_status.value,
                duplicate_of_document_id=duplicate_document_id,
                duplicate_type=duplicate_type,
                document_id=duplicate_document_id,
                file_path=file_path,
                file_name=file_name,
            ),
            event_context=event_context,
        )
        return IngestionResult(
            status=duplicate_status,
            ingestion_run_id=ingestion_run.run_id,
            document_id=duplicate_document_id,
            file_name=file_name,
            duplicate_of_document_id=duplicate_document_id,
            warnings=warnings,
            diagnostics={
                "file_path": file_path,
                "file_hash": file_hash,
                "content_hash": content_hash,
                "metadata": dict(request.metadata),
                **self.runtime_diagnostics_loader(),
            },
            current_stage=current_stage,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _status_for_duplicate_type(duplicate_type: str) -> IngestionStatus:
        if duplicate_type == "file_hash":
            return IngestionStatus.SKIPPED_FILE_DUPLICATE
        return IngestionStatus.SKIPPED_CONTENT_DUPLICATE

    def handle_stale_redirect(
        self,
        *,
        ingestion_run: IngestionRun,
        target_document_id: str,
        file_name: str,
        file_path: str,
        event_context: EventContext | None,
    ) -> None:
        """Finalizes the in-flight ingestion_run as redirected (not failed,
        not a plain skip) before the caller raises StaleParserVersionDetected
        to hand off to IngestionWorkflow.reingest() for target_document_id.
        """
        ingestion_run.status = IngestionStatus.REDIRECTED_STALE_PARSER_VERSION
        ingestion_run.document_id = target_document_id
        ingestion_run.finished_at = datetime.now(UTC)
        self.run_store.update(ingestion_run)
        self.event_publisher.publish_event(
            IngestionEvent.redirected_stale_parser_version(
                event_id=self.id_generator.new_event_id(),
                ingestion_run_id=ingestion_run.run_id,
                target_document_id=target_document_id,
                document_id=target_document_id,
                file_path=file_path,
                file_name=file_name,
            ),
            event_context=event_context,
        )
