import json

from src.domain.activity import ActivityRecord
from src.infrastructure.db.orm_models import ActivityRecordORM
from src.shared.activity import ActivitySeverity, ActivityStatus


class ActivityRecordMapper:
    @staticmethod
    def to_orm(activity: ActivityRecord) -> ActivityRecordORM:
        return ActivityRecordORM(
            id=activity.activity_id,
            action=activity.action,
            message=activity.message,
            entity_type=activity.entity_type,
            entity_id=activity.entity_id,
            status=activity.status.value,
            severity=activity.severity.value,
            actor_id=activity.actor_id,
            actor_type=activity.actor_type,
            request_id=activity.request_id,
            correlation_id=activity.correlation_id,
            source=activity.source,
            payload_json=json.dumps(activity.payload),
            created_at=activity.created_at,
        )

    @staticmethod
    def to_domain(orm: ActivityRecordORM) -> ActivityRecord:
        return ActivityRecord(
            activity_id=orm.id,
            action=orm.action,
            message=orm.message,
            entity_type=orm.entity_type,
            entity_id=orm.entity_id,
            status=ActivityStatus(orm.status),
            severity=ActivitySeverity(orm.severity),
            actor_id=orm.actor_id,
            actor_type=orm.actor_type,
            request_id=orm.request_id,
            correlation_id=orm.correlation_id,
            source=orm.source,
            payload=json.loads(orm.payload_json or "{}"),
            created_at=orm.created_at,
        )