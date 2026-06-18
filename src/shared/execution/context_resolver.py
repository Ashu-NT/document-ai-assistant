from typing import Any

from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext


def resolve_activity_context(kwargs: dict[str, Any]) -> ActivityContext:
    context = kwargs.get("activity_context")

    if isinstance(context, ActivityContext):
        return context

    return ActivityContext()


def resolve_audit_context(kwargs: dict[str, Any]) -> AuditContext:
    context = kwargs.get("audit_context")

    if isinstance(context, AuditContext):
        return context

    return AuditContext()