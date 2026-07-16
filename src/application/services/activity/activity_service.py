from src.application.contracts.activity import ActivityRepository
from src.domain.activity import ActivityRecord
from src.shared.activity import ActivityContext, ActivityPayload, ActivityStatus
from src.shared.activity.activity_builder import ActivityBuilder
from src.shared.severity import Severity


class ActivityService:
    def __init__(self, repository: ActivityRepository) -> None:
        self.repository = repository

    def record(
        self,
        *,
        action: str,
        message: str,
        context: ActivityContext | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        status: ActivityStatus = ActivityStatus.COMPLETED,
        severity: Severity = Severity.INFO,
        payload: ActivityPayload | None = None,
    ) -> ActivityRecord:
        activity = ActivityBuilder.build(
            action=action,
            message=message,
            context=context,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            severity=severity,
            payload=payload,
        )

        self.repository.save(activity)

        return activity