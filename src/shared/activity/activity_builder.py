from src.domain.activity.activity_record import ActivityRecord
from src.shared.activity.activity_context import ActivityContext
from src.shared.activity.activity_payload import ActivityPayload
from src.shared.activity.activity_types import ActivitySeverity, ActivityStatus


class ActivityBuilder:
    @staticmethod
    def build(
        *,
        action: str,
        message: str,
        context: ActivityContext | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        status: ActivityStatus = ActivityStatus.COMPLETED,
        severity: ActivitySeverity = ActivitySeverity.INFO,
        payload: ActivityPayload | None = None,
    ) -> ActivityRecord:
        context = context or ActivityContext()

        return ActivityRecord(
            action=action,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            severity=severity,
            actor_id=context.actor_id,
            actor_type=context.actor_type,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            source=context.source,
            payload=payload or {},
        )