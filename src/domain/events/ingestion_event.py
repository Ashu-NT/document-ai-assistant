from dataclasses import dataclass, field

from src.domain.events.domain_event import DomainEvent


@dataclass(slots=True)
class IngestionEvent(DomainEvent):
    document_id: str | None = None
    ingestion_run_id: str | None = None
    status: str | None = None
    stage: str | None = None
    file_path: str | None = None
    file_name: str | None = None

    @classmethod
    def started(
        cls,
        event_id: str,
        ingestion_run_id: str,
        document_id: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.started",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="started",
            file_path=file_path,
            file_name=file_name,
        )

    @classmethod
    def stage_started(
        cls,
        event_id: str,
        ingestion_run_id: str,
        *,
        stage: str,
        document_id: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.stage.started",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="started",
            stage=stage,
            file_path=file_path,
            file_name=file_name,
        )

    @classmethod
    def stage_completed(
        cls,
        event_id: str,
        ingestion_run_id: str,
        *,
        stage: str,
        status: str,
        document_id: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
        payload: dict | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.stage.completed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status=status,
            stage=stage,
            file_path=file_path,
            file_name=file_name,
            payload=payload or {},
        )

    @classmethod
    def skipped_duplicate(
        cls,
        event_id: str,
        ingestion_run_id: str,
        *,
        status: str,
        duplicate_of_document_id: str,
        duplicate_type: str,
        document_id: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.skipped_duplicate",
            aggregate_id=document_id or duplicate_of_document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status=status,
            file_path=file_path,
            file_name=file_name,
            payload={
                "duplicate_of_document_id": duplicate_of_document_id,
                "duplicate_type": duplicate_type,
            },
        )

    @classmethod
    def completed(
        cls,
        event_id: str,
        ingestion_run_id: str,
        document_id: str,
        file_path: str | None = None,
        file_name: str | None = None,
        payload: dict | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.completed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="completed",
            file_path=file_path,
            file_name=file_name,
            payload=payload or {},
        )

    @classmethod
    def failed(
        cls,
        event_id: str,
        ingestion_run_id: str,
        error_message: str,
        document_id: str | None = None,
        stage: str | None = None,
        file_path: str | None = None,
        file_name: str | None = None,
        details: dict | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.failed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="failed",
            stage=stage,
            file_path=file_path,
            file_name=file_name,
            payload={
                "error_message": error_message,
                **(details or {}),
            },
        )
