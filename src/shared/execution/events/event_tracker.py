from typing import Any, TYPE_CHECKING

from src.domain.events import DomainEvent
from src.shared.events import EventContext, EventSeverity
from src.shared.execution.action_result import ActionResult
from src.shared.execution.payloads import build_failure_payload

if TYPE_CHECKING:
    from src.application.services.events import EventService

class EventTracker:
    @staticmethod
    def record_success(
        *,
        service_instance: Any,
        action: str,
        context: EventContext,
        result: Any,
        default_entity_type: str | None,
    ) -> None:
        event_service:EventService = getattr(service_instance, "event_service", None)

        if event_service is None:
            return

        if isinstance(result, DomainEvent):
            event_service.publish(
                result,
                context=context,
                severity=EventSeverity.INFO,
            )
            return

        if isinstance(result, ActionResult):
            event = DomainEvent(
                event_id=result.event_id,
                event_type=action,
                aggregate_type=result.entity_type or default_entity_type,
                aggregate_id=result.entity_id,
                payload=result.payload,
            )
            event_service.publish(event, context=context)
            return

    @staticmethod
    def record_failure(
        *,
        service_instance: Any,
        action: str,
        context: EventContext,
        exc: Exception,
        default_entity_type: str | None,
    ) -> None:
        event_service = getattr(service_instance, "event_service", None)

        if event_service is None:
            return

        event = DomainEvent(
            event_type=f"{action}.failed",
            aggregate_type=default_entity_type,
            payload=build_failure_payload(exc),
        )

        event_service.publish(
            event,
            context=context,
            severity=EventSeverity.ERROR,
        )