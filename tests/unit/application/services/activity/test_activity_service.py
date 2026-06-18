from src.application.services.activity import ActivityService
from src.shared.activity import ActivityContext


class FakeActivityRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, activity) -> None:
        self.saved.append(activity)

    def list_by_entity(self, entity_type: str, entity_id: str, limit: int = 50):
        return []


def test_activity_service_records_activity() -> None:
    repository = FakeActivityRepository()
    service = ActivityService(repository)

    activity = service.record(
        action="document.uploaded",
        message="Document uploaded.",
        context=ActivityContext(
            actor_id="user_001",
            request_id="req_001",
        ),
        entity_type="document",
        entity_id="doc_001",
        payload={"file_name": "manual.pdf"},
    )

    assert activity.action == "document.uploaded"
    assert activity.actor_id == "user_001"
    assert len(repository.saved) == 1