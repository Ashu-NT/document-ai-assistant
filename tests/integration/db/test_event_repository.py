from datetime import datetime, timezone

from src.shared.events import EventEnvelope, EventSeverity, EventStatus


def test_event_repository_saves_and_lists_by_aggregate(db_uow) -> None:
    event = EventEnvelope(
        event_id="event_001",
        event_type="classification.completed",
        aggregate_type="document",
        aggregate_id="doc_001",
        status=EventStatus.PENDING,
        severity=EventSeverity.INFO,
        payload={"classification_id": "classification_001"},
        occurred_at=datetime.now(timezone.utc),
    )

    db_uow.events.save(event)
    db_uow.commit()

    events = db_uow.events.list_by_aggregate(
        aggregate_type="document",
        aggregate_id="doc_001",
    )

    assert len(events) == 1
    assert events[0].event_type == "classification.completed"
    assert events[0].payload["classification_id"] == "classification_001"