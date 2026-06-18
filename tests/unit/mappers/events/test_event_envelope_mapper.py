from datetime import datetime, timezone

from src.infrastructure.db.mappers.events import EventEnvelopeMapper
from src.shared.events import EventEnvelope, EventSeverity, EventStatus


def test_event_envelope_mapper_round_trip() -> None:
    event = EventEnvelope(
        event_id="event_001",
        event_type="classification.completed",
        aggregate_type="document",
        aggregate_id="doc_001",
        status=EventStatus.PENDING,
        severity=EventSeverity.INFO,
        actor_id="user_001",
        payload={"classification_id": "classification_001"},
        occurred_at=datetime.now(timezone.utc),
    )

    orm = EventEnvelopeMapper.to_orm(event)
    domain = EventEnvelopeMapper.to_domain(orm)

    assert domain.event_id == event.event_id
    assert domain.event_type == event.event_type
    assert domain.aggregate_id == event.aggregate_id
    assert domain.payload["classification_id"] == "classification_001"