from src.shared.activity import (
    ActivityContext,
    ActivitySeverity,
    ActivityStatus,
)
from src.shared.activity.activity_builder import ActivityBuilder

def test_activity_builder_builds_record_with_context() -> None:
    context = ActivityContext(
        actor_id="user_001",
        actor_type="user",
        request_id="req_001",
        correlation_id="corr_001",
        source="cli",
    )

    activity = ActivityBuilder.build(
        action="document.uploaded",
        message="Document uploaded.",
        context=context,
        entity_type="document",
        entity_id="doc_001",
        status=ActivityStatus.COMPLETED,
        severity=ActivitySeverity.INFO,
        payload={"file_name": "manual.pdf"},
    )

    assert activity.action == "document.uploaded"
    assert activity.actor_id == "user_001"
    assert activity.actor_type == "user"
    assert activity.request_id == "req_001"
    assert activity.correlation_id == "corr_001"
    assert activity.source == "cli"
    assert activity.entity_id == "doc_001"
    assert activity.payload["file_name"] == "manual.pdf"


def test_activity_builder_uses_default_context() -> None:
    activity = ActivityBuilder.build(
        action="system.started",
        message="System started.",
    )

    assert activity.actor_type == "system"
    assert activity.status == ActivityStatus.COMPLETED
    assert activity.severity == ActivitySeverity.INFO
    assert activity.payload == {}