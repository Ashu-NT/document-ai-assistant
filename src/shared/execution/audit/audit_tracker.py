from typing import Any

from src.shared.audit import AuditContext, AuditOutcome, AuditSeverity
from src.shared.execution.action_result import ActionResult
from src.shared.execution.payloads import build_failure_payload


class AuditTracker:
    @staticmethod
    def record_success(
        *,
        service_instance: Any,
        action: str,
        context: AuditContext,
        result: Any,
        default_entity_type: str | None,
    ) -> None:
        audit_service = getattr(service_instance, "audit_service", None)

        if audit_service is None:
            return

        action_result = (
            result
            if isinstance(result, ActionResult)
            else ActionResult(entity_type=default_entity_type)
        )

        audit_service.record(
            action=action,
            context=context,
            entity_type=action_result.entity_type or default_entity_type,
            entity_id=action_result.entity_id,
            outcome=AuditOutcome.SUCCESS,
            severity=AuditSeverity.LOW,
            after_state=action_result.payload,
            metadata={"message": action_result.message},
        )

    @staticmethod
    def record_failure(
        *,
        service_instance: Any,
        action: str,
        context: AuditContext,
        exc: Exception,
        default_entity_type: str | None,
    ) -> None:
        audit_service = getattr(service_instance, "audit_service", None)

        if audit_service is None:
            return

        audit_service.record(
            action=action,
            context=context,
            entity_type=default_entity_type,
            outcome=AuditOutcome.FAILURE,
            severity=AuditSeverity.HIGH,
            metadata=build_failure_payload(exc),
        )