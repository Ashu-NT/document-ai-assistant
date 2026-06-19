from typing import Any

from src.shared.activity import ActivityContext, ActivitySeverity, ActivityStatus
from src.shared.execution.payloads import build_failure_payload
from src.shared.execution.result_adapter import ResultAdapter


class ActivityTracker:
    @staticmethod
    def record_success(
        *,
        service_instance: Any,
        action: str,
        context: ActivityContext,
        result: Any,
        default_entity_type: str | None,
    ) -> None:
        activity_service = getattr(service_instance, "activity_service", None)

        if activity_service is None:
            return

        action_result = ResultAdapter.to_action_result(
            result,
            default_entity_type=default_entity_type,
        )

        activity_service.record(
            action=action,
            message=action_result.message or f"{action} completed.",
            context=context,
            entity_type=action_result.entity_type or default_entity_type,
            entity_id=action_result.entity_id,
            status=ActivityStatus.COMPLETED,
            severity=ActivitySeverity.INFO,
            payload=action_result.payload,
        )

    @staticmethod
    def record_failure(
        *,
        service_instance: Any,
        action: str,
        context: ActivityContext,
        exc: Exception,
        default_entity_type: str | None,
    ) -> None:
        activity_service = getattr(service_instance, "activity_service", None)

        if activity_service is None:
            return

        activity_service.record(
            action=action,
            message=f"{action} failed.",
            context=context,
            entity_type=default_entity_type,
            status=ActivityStatus.FAILED,
            severity=ActivitySeverity.ERROR,
            payload=build_failure_payload(exc),
        )
