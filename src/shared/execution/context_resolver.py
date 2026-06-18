from typing import Any

from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.events import EventContext


def resolve_activity_context(kwargs: dict[str, Any]) -> ActivityContext:
    context = kwargs.get("activity_context")
    return context if isinstance(context, ActivityContext) else ActivityContext()


def resolve_audit_context(kwargs: dict[str, Any]) -> AuditContext:
    context = kwargs.get("audit_context")
    return context if isinstance(context, AuditContext) else AuditContext()


def resolve_event_context(kwargs: dict[str, Any]) -> EventContext:
    context = kwargs.get("event_context")
    return context if isinstance(context, EventContext) else EventContext()