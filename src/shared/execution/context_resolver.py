from typing import Any

from src.shared.activity import ActivityContext


def resolve_activity_context(kwargs: dict[str, Any]) -> ActivityContext:
    context = kwargs.get("activity_context")

    if isinstance(context, ActivityContext):
        return context

    return ActivityContext()