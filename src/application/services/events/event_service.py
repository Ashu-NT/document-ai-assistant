from src.application.contracts.events import EventRepository
from src.domain.events import DomainEvent
from src.shared.events import EventContext, EventEnvelope, EventSeverity
from src.shared.events.domain_event_serializer import DomainEventSerializer


class EventService:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def publish(
        self,
        event: DomainEvent,
        *,
        context: EventContext | None = None,
        severity: EventSeverity = EventSeverity.INFO,
    ) -> EventEnvelope:
        context = context or EventContext()

        envelope = EventEnvelope(
            event_id=event.event_id,
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            severity=severity,
            actor_id=context.actor_id,
            actor_type=context.actor_type,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            source=context.source,
            payload=DomainEventSerializer.to_payload(event),
            occurred_at=event.occurred_at,
        )

        self.repository.save(envelope)

        return envelope