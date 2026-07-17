from __future__ import annotations

from typing import Callable

from src.application.workflows.ingestion.ingestion_request import IngestionRequest
from src.application.workflows.ingestion.ingestion_result import IngestionResult
from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus
from src.domain.workflow import IngestionRun
from src.shared.events import EventContext

from .duplicate_check_step import DuplicateCheckStep
from .duplicate_ingestion_exit_handler import DuplicateIngestionExitHandler


class IngestionDuplicateCoordinator:
    def __init__(
        self,
        *,
        duplicate_check_step: DuplicateCheckStep,
        duplicate_exit_handler: DuplicateIngestionExitHandler,
        event_publisher,
    ) -> None:
        self.duplicate_check_step = duplicate_check_step
        self.duplicate_exit_handler = duplicate_exit_handler
        self.event_publisher = event_publisher

    def check_file_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        ingestion_run: IngestionRun,
        file_name: str,
        file_path: str,
        file_hash: str,
        correlation_id: str,
        warnings: list[str],
        activity_context,
        event_context: EventContext | None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> IngestionResult | None:
        self.event_publisher.publish_stage_started(
            ingestion_run=ingestion_run,
            stage=IngestionStage.DUPLICATE_CHECK,
            event_context=event_context,
            file_name=file_name,
            progress_callback=progress_callback,
        )
        duplicate_document_id = self.duplicate_check_step.check_file_hash_duplicate(
            request=request,
            file_hash=file_hash,
            activity_context=activity_context,
        )
        if duplicate_document_id is None:
            self.event_publisher.publish_stage_completed(
                ingestion_run=ingestion_run,
                stage=IngestionStage.DUPLICATE_CHECK,
                status=ingestion_run.status,
                event_context=event_context,
                file_name=file_name,
                payload={"duplicate": False},
            )
            return None

        ingestion_run.status = IngestionStatus.SKIPPED_FILE_DUPLICATE
        self.event_publisher.publish_stage_completed(
            ingestion_run=ingestion_run,
            stage=IngestionStage.DUPLICATE_CHECK,
            status=ingestion_run.status,
            event_context=event_context,
            file_name=file_name,
            payload={"duplicate": True, "type": "file_hash"},
        )
        return self.duplicate_exit_handler.handle(
            request=request,
            ingestion_run=ingestion_run,
            duplicate_document_id=duplicate_document_id,
            duplicate_type="file_hash",
            current_stage=IngestionStage.DUPLICATE_CHECK,
            file_name=file_name,
            file_path=file_path,
            file_hash=file_hash,
            content_hash=None,
            correlation_id=correlation_id,
            warnings=warnings,
            event_context=event_context,
        )

    def check_content_hash_duplicate(
        self,
        *,
        request: IngestionRequest,
        ingestion_run: IngestionRun,
        duplicate_stage: IngestionStage,
        file_name: str,
        file_path: str,
        file_hash: str,
        content_hash: str,
        correlation_id: str,
        warnings: list[str],
        activity_context,
        event_context: EventContext | None,
    ) -> IngestionResult | None:
        duplicate_document_id = self.duplicate_check_step.check_content_hash_duplicate(
            request=request,
            content_hash=content_hash,
            activity_context=activity_context,
        )
        if duplicate_document_id is None:
            return None
        return self.duplicate_exit_handler.handle(
            request=request,
            ingestion_run=ingestion_run,
            duplicate_document_id=duplicate_document_id,
            duplicate_type="content_hash",
            current_stage=duplicate_stage,
            file_name=file_name,
            file_path=file_path,
            file_hash=file_hash,
            content_hash=content_hash,
            correlation_id=correlation_id,
            warnings=warnings,
            event_context=event_context,
        )
