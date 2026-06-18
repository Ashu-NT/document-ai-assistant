from src.application.services.events import EventService
from src.domain.events.classification_event import ClassificationEvent
from src.shared.events import EventContext


class FakeEventRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, event) -> None:
        self.saved.append(event)

    def list_by_aggregate(self, aggregate_type: str, aggregate_id: str, limit: int = 50):
        return []


def test_event_service_publishes_domain_event() -> None:
    repository = FakeEventRepository()
    service = EventService(repository)

    domain_event = ClassificationEvent.completed(
        event_id="event_001",
        document_id="doc_001",
        classification_id="classification_001",
        predicted_label="manual",
        confidence_score=0.91,
    )

    envelope = service.publish(
        domain_event,
        context=EventContext(
            actor_id="user_001",
            request_id="req_001",
        ),
    )

    assert envelope.event_id == "event_001"
    assert envelope.event_type == "classification.completed"
    assert envelope.aggregate_id == "doc_001"
    assert envelope.actor_id == "user_001"
    assert envelope.payload["classification_id"] == "classification_001"
    assert len(repository.saved) == 1