from collections.abc import Callable
from functools import wraps
from typing import Any

from src.shared.execution.activity import ActivityTracker
from src.shared.execution.audit import AuditTracker
from src.shared.execution.context_resolver import (
    resolve_activity_context,
    resolve_audit_context,
    resolve_event_context,
)
from src.shared.execution.events import EventTracker
from src.shared.execution.tracking_options import TrackingOptions


def tracked_action(
    *,
    action: str,
    entity_type: str | None = None,
    activity: bool = True,
    audit: bool = False,
    event: bool = False,
) -> Callable:
    options = TrackingOptions(
        activity=activity,
        audit=audit,
        event=event,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            activity_context = resolve_activity_context(kwargs)
            audit_context = resolve_audit_context(kwargs)
            event_context = resolve_event_context(kwargs)
            try:
                result = func(self, *args, **kwargs)

                if options.activity:
                    ActivityTracker.record_success(
                        service_instance=self,
                        action=action,
                        context=activity_context,
                        result=result,
                        default_entity_type=entity_type,
                    )

                if options.audit:
                    AuditTracker.record_success(
                        service_instance=self,
                        action=action,
                        context=audit_context,
                        result=result,
                        default_entity_type=entity_type,
                    )
                    
                if options.event:
                    EventTracker.record_success(
                        service_instance=self,
                        action=action,
                        context=event_context,
                        result=result,
                        default_entity_type=entity_type,
                    )

                return result

            except Exception as exc:
                if options.activity:
                    ActivityTracker.record_failure(
                        service_instance=self,
                        action=action,
                        context=activity_context,
                        exc=exc,
                        default_entity_type=entity_type,
                    )

                if options.audit:
                    AuditTracker.record_failure(
                        service_instance=self,
                        action=action,
                        context=audit_context,
                        exc=exc,
                        default_entity_type=entity_type,
                    )
                    
                if options.event:
                    EventTracker.record_failure(
                        service_instance=self,
                        action=action,
                        context=event_context,
                        exc=exc,
                        default_entity_type=entity_type,
                    )

                raise

        return wrapper

    return decorator