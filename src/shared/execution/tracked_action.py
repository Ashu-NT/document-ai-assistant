from collections.abc import Callable
from functools import wraps
from typing import Any

from src.shared.execution.activity import ActivityTracker
from src.shared.execution.context_resolver import resolve_activity_context
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
            context = resolve_activity_context(kwargs)

            try:
                result = func(self, *args, **kwargs)

                if options.activity:
                    ActivityTracker.record_success(
                        service_instance=self,
                        action=action,
                        context=context,
                        result=result,
                        default_entity_type=entity_type,
                    )

                return result

            except Exception as exc:
                if options.activity:
                    ActivityTracker.record_failure(
                        service_instance=self,
                        action=action,
                        context=context,
                        exc=exc,
                        default_entity_type=entity_type,
                    )

                raise

        return wrapper

    return decorator