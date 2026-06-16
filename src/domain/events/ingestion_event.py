from dataclasses import dataclass, field

from src.domain.events.domain_event import DomainEvent


@dataclass(slots=True)
class IngestionEvent(DomainEvent):
    document_id: str | None = None
    ingestion_run_id: str | None = None
    status: str | None = None

    @classmethod
    def started(
        cls,
        event_id: str,
        ingestion_run_id: str,
        document_id: str | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.started",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="started",
        )

    @classmethod
    def completed(
        cls,
        event_id: str,
        ingestion_run_id: str,
        document_id: str,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.completed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="completed",
        )

    @classmethod
    def failed(
        cls,
        event_id: str,
        ingestion_run_id: str,
        error_message: str,
        document_id: str | None = None,
    ) -> "IngestionEvent":
        return cls(
            event_id=event_id,
            event_type="ingestion.failed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            ingestion_run_id=ingestion_run_id,
            status="failed",
            payload={"error_message": error_message},
        )