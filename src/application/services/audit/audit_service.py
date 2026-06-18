from src.application.contracts.audit import AuditRepository
from src.domain.audit import AuditRecord
from src.shared.audit import AuditContext, AuditOutcome, AuditSeverity


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def record(
        self,
        *,
        action: str,
        context: AuditContext | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        outcome: AuditOutcome = AuditOutcome.SUCCESS,
        severity: AuditSeverity = AuditSeverity.LOW,
        before_state: dict | None = None,
        after_state: dict | None = None,
        metadata: dict | None = None,
    ) -> AuditRecord:
        context = context or AuditContext()

        audit = AuditRecord(
            action=action,
            outcome=outcome,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=context.actor_id,
            actor_type=context.actor_type,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            source=context.source,
            ip_address=context.ip_address,
            before_state=before_state,
            after_state=after_state,
            metadata=metadata or {},
        )

        self.repository.save(audit)

        return audit