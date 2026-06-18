import json

from src.infrastructure.db.orm_models import EventEnvelopeORM
from src.shared.events import EventEnvelope, EventSeverity, EventStatus


class EventEnvelopeMapper:
    @staticmethod
    def to_orm(event: EventEnvelope) -> EventEnvelopeORM:
        return EventEnvelopeORM(
            id=event.event_id,
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            status=event.status.value,
            severity=event.severity.value,
            actor_id=event.actor_id,
            actor_type=event.actor_type,
            request_id=event.request_id,
            correlation_id=event.correlation_id,
            source=event.source,
            payload_json=json.dumps(event.payload),
            occurred_at=event.occurred_at,
            published_at=event.published_at,
        )

    @staticmethod
    def to_domain(orm: EventEnvelopeORM) -> EventEnvelope:
        return EventEnvelope(
            event_id=orm.id,
            event_type=orm.event_type,
            aggregate_type=orm.aggregate_type,
            aggregate_id=orm.aggregate_id,
            status=EventStatus(orm.status),
            severity=EventSeverity(orm.severity),
            actor_id=orm.actor_id,
            actor_type=orm.actor_type,
            request_id=orm.request_id,
            correlation_id=orm.correlation_id,
            source=orm.source,
            payload=json.loads(orm.payload_json or "{}"),
            occurred_at=orm.occurred_at,
            published_at=orm.published_at,
        )