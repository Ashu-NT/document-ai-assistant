from dataclasses import dataclass

from src.domain.events.domain_event import DomainEvent


@dataclass(slots=True)
class RetrievalEvent(DomainEvent):
    query_id: str | None = None
    result_id: str | None = None
    result_count: int = 0
    best_score: float | None = None

    @classmethod
    def completed(
        cls,
        event_id: str,
        query_id: str,
        result_id: str,
        result_count: int,
        best_score: float | None = None,
    ) -> "RetrievalEvent":
        return cls(
            event_id=event_id,
            event_type="retrieval.completed",
            aggregate_id=query_id,
            aggregate_type="retrieval_query",
            query_id=query_id,
            result_id=result_id,
            result_count=result_count,
            best_score=best_score,
        )