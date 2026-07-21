from __future__ import annotations

from src.application.workflows.ingestion.models.ingestion_request import IngestionRequest
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.events import EventContext


def resolve_activity_context(
    *,
    request: IngestionRequest,
    correlation_id: str,
    activity_context: ActivityContext | None,
) -> ActivityContext:
    """Return the caller-supplied activity context unchanged, or build a
    default one scoped to this ingestion request/correlation id.
    """
    if activity_context is not None:
        return activity_context
    return ActivityContext(
        actor_id=request.requested_by,
        actor_type="user" if request.requested_by else "system",
        request_id=correlation_id,
        correlation_id=correlation_id,
        source="ingestion_workflow",
    )


def resolve_audit_context(
    *,
    request: IngestionRequest,
    correlation_id: str,
    audit_context: AuditContext | None,
) -> AuditContext:
    """Return the caller-supplied audit context unchanged, or build a
    default one scoped to this ingestion request/correlation id.
    """
    if audit_context is not None:
        return audit_context
    return AuditContext(
        actor_id=request.requested_by,
        actor_type="user" if request.requested_by else "system",
        request_id=correlation_id,
        correlation_id=correlation_id,
        source="ingestion_workflow",
    )


def resolve_event_context(
    *,
    request: IngestionRequest,
    correlation_id: str,
    event_context: EventContext | None,
) -> EventContext:
    """Return the caller-supplied event context unchanged, or build a
    default one scoped to this ingestion request/correlation id.
    """
    if event_context is not None:
        return event_context
    return EventContext(
        actor_id=request.requested_by,
        actor_type="user" if request.requested_by else "system",
        request_id=correlation_id,
        correlation_id=correlation_id,
        source="ingestion_workflow",
    )
