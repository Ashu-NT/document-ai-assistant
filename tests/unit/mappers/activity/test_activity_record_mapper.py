from src.domain.activity import ActivityRecord
from src.infrastructure.db.mappers import ActivityRecordMapper
from src.shared.activity import ActivityContext, ActivityStatus


def test_activity_record_mapper_round_trip() -> None:
    activity = ActivityRecord(
        action="document.uploaded",
        message="Document uploaded.",
        entity_type="document",
        entity_id="doc_001",
        status=ActivityStatus.COMPLETED,
        actor_id="user_001",
        payload={"file_name": "manual.pdf"},
    )

    orm = ActivityRecordMapper.to_orm(activity)
    domain = ActivityRecordMapper.to_domain(orm)

    assert domain.activity_id == activity.activity_id
    assert domain.action == activity.action
    assert domain.entity_id == activity.entity_id
    assert domain.payload["file_name"] == "manual.pdf"