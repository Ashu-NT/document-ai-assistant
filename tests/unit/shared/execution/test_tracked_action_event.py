import pytest

from src.domain.events import DomainEvent
from src.shared.events import EventContext, EventSeverity
from src.shared.execution import ActionResult, tracked_action


class FakeEventService:
    def __init__(self) -> None:
        self.published = []

    def publish(self, event, *, context=None, severity=EventSeverity.INFO):
        self.published.append(
            {
                "event": event,
                "context": context,
                "severity": severity,
            }
        )


class ExampleEventService:
    def __init__(self) -> None:
        self.event_service = FakeEventService()

    @tracked_action(
        action="document.loaded",
        entity_type="document",
        activity=False,
        audit=False,
        event=True,
    )
    def load_document(self, document_id: str, event_context=None):
        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Document loaded.",
            payload={"document_id": document_id},
        )

    @tracked_action(
        action="document.classified",
        entity_type="document",
        activity=False,
        audit=False,
        event=True,
    )
    def classify_document(self, event_context=None):
        return DomainEvent(
            event_id="event_001",
            event_type="classification.completed",
            aggregate_type="document",
            aggregate_id="doc_001",
            payload={"classification_id": "classification_001"},
        )

    @tracked_action(
        action="document.load",
        entity_type="document",
        activity=False,
        audit=False,
        event=True,
    )
    def fail(self, event_context=None):
        raise RuntimeError("load failed")


def test_tracked_action_records_event_from_action_result() -> None:
    service = ExampleEventService()

    service.load_document(
        "doc_001",
        event_context=EventContext(actor_id="user_001"),
    )

    assert len(service.event_service.published) == 1

    published = service.event_service.published[0]
    event = published["event"]

    assert event.event_type == "document.loaded"
    assert event.aggregate_type == "document"
    assert event.aggregate_id == "doc_001"
    assert event.payload["document_id"] == "doc_001"
    assert published["context"].actor_id == "user_001"
    assert published["severity"] == EventSeverity.INFO


def test_tracked_action_records_existing_domain_event() -> None:
    service = ExampleEventService()

    service.classify_document(
        event_context=EventContext(actor_id="user_001"),
    )

    assert len(service.event_service.published) == 1

    published = service.event_service.published[0]
    event = published["event"]

    assert event.event_type == "classification.completed"
    assert event.aggregate_id == "doc_001"
    assert event.payload["classification_id"] == "classification_001"


def test_tracked_action_records_event_failure() -> None:
    service = ExampleEventService()

    with pytest.raises(RuntimeError):
        service.fail(event_context=EventContext(actor_id="user_001"))

    assert len(service.event_service.published) == 1

    published = service.event_service.published[0]
    event = published["event"]

    assert event.event_type == "document.load.failed"
    assert event.aggregate_type == "document"
    assert event.payload["error_type"] == "RuntimeError"
    assert published["severity"] == EventSeverity.ERROR