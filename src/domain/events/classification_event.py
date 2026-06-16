from dataclasses import dataclass

from src.domain.events.domain_event import DomainEvent


@dataclass(slots=True)
class ClassificationEvent(DomainEvent):
    document_id: str | None = None
    classification_id: str | None = None
    predicted_label: str | None = None
    confidence_score: float | None = None

    @classmethod
    def completed(
        cls,
        event_id: str,
        document_id: str,
        classification_id: str,
        predicted_label: str,
        confidence_score: float | None = None,
    ) -> "ClassificationEvent":
        return cls(
            event_id=event_id,
            event_type="classification.completed",
            aggregate_id=document_id,
            aggregate_type="document",
            document_id=document_id,
            classification_id=classification_id,
            predicted_label=predicted_label,
            confidence_score=confidence_score,
        )