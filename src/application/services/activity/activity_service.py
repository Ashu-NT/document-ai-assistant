from src.application.contracts.activity import ActivityRepository
from src.domain.activity import ActivityRecord
from src.shared.activity import ActivityContext, ActivityPayload


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
        payload: ActivityPayload | None = None,
    ) -> ActivityRecord:
        context = context or ActivityContext()

        activity = ActivityRecord(
            action=action,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=context.actor_id,
            actor_type=context.actor_type,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            source=context.source,
            payload=payload or {},
        )

        self.repository.save(activity)

        return activity