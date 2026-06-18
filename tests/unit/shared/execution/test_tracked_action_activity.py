import pytest

from src.shared.activity import ActivityContext, ActivityStatus
from src.shared.execution import ActionResult, tracked_action


class FakeActivityService:
    def __init__(self) -> None:
        self.records = []

    def record(self, **kwargs):
        self.records.append(kwargs)


class ExampleService:
    def __init__(self) -> None:
        self.activity_service = FakeActivityService()

    @tracked_action(action="document.loaded", entity_type="document")
    def load_document(self, document_id: str, activity_context=None):
        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Document loaded.",
            payload={"document_id": document_id},
        )

    @tracked_action(action="document.failed", entity_type="document")
    def fail(self, activity_context=None):
        raise RuntimeError("boom")


def test_tracked_action_records_activity_success() -> None:
    service = ExampleService()

    service.load_document(
        "doc_001",
        activity_context=ActivityContext(actor_id="user_001"),
    )

    assert len(service.activity_service.records) == 1

    record = service.activity_service.records[0]

    assert record["action"] == "document.loaded"
    assert record["message"] == "Document loaded."
    assert record["entity_id"] == "doc_001"
    assert record["status"] == ActivityStatus.COMPLETED
    assert record["payload"]["document_id"] == "doc_001"


def test_tracked_action_records_activity_failure() -> None:
    service = ExampleService()

    with pytest.raises(RuntimeError):
        service.fail(activity_context=ActivityContext(actor_id="user_001"))

    assert len(service.activity_service.records) == 1

    record = service.activity_service.records[0]

    assert record["action"] == "document.failed"
    assert record["status"] == ActivityStatus.FAILED
    assert record["payload"]["error_type"] == "RuntimeError"


def test_tracked_action_can_disable_activity() -> None:
    class ServiceWithoutActivityTracking:
        def __init__(self) -> None:
            self.activity_service = FakeActivityService()

        @tracked_action(
            action="document.silent",
            entity_type="document",
            activity=False,
        )
        def execute(self, activity_context=None):
            return ActionResult(entity_id="doc_001")

    service = ServiceWithoutActivityTracking()

    service.execute()

    assert service.activity_service.records == []