from typing import Protocol

from src.shared.events import EventEnvelope


class EventRepository(Protocol):
    def save(self, event: EventEnvelope) -> None:
        ...

    def list_by_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: str,
        limit: int = 50,
    ) -> list[EventEnvelope]:
        ...