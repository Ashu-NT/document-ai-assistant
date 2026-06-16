from dataclasses import dataclass

from src.domain.events.domain_event import DomainEvent


@dataclass(slots=True)
class ExtractionEvent(DomainEvent):
    document_id: str | None = None
    extraction_id: str | None = None
    extracted_count: int = 0
    extraction_type: str | None = None

    @classmethod
    def completed(
        cls,
        event_id: str,
        document_id: str,
        extraction_id: str,
        extraction_type: str,
        extracted_count: int,
    ) -> "ExtractionEvent":
        return cls(
            event_id=event_id,
            event_type="extraction.completed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            extraction_id=extraction_id,
            extraction_type=extraction_type,
            extracted_count=extracted_count,
        )