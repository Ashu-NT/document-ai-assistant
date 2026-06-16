from typing import Protocol

from src.domain.events import DomainEvent


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None:
        ...

    def publish_many(self, events: list[DomainEvent]) -> None:
        ...