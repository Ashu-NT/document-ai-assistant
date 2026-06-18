import json

from src.domain.audit import AuditRecord
from src.infrastructure.db.orm_models import AuditRecordORM
from src.shared.audit import AuditOutcome, AuditSeverity


class AuditRecordMapper:
    @staticmethod
    def to_orm(audit: AuditRecord) -> AuditRecordORM:
        return AuditRecordORM(
            id=audit.audit_id,
            action=audit.action,
            outcome=audit.outcome.value,
            severity=audit.severity.value,
            entity_type=audit.entity_type,
            entity_id=audit.entity_id,
            actor_id=audit.actor_id,
            actor_type=audit.actor_type,
            request_id=audit.request_id,
            correlation_id=audit.correlation_id,
            source=audit.source,
            ip_address=audit.ip_address,
            before_state_json=json.dumps(audit.before_state)
            if audit.before_state is not None
            else None,
            after_state_json=json.dumps(audit.after_state)
            if audit.after_state is not None
            else None,
            metadata_json=json.dumps(audit.metadata),
            created_at=audit.created_at,
        )

    @staticmethod
    def to_domain(orm: AuditRecordORM) -> AuditRecord:
        return AuditRecord(
            audit_id=orm.id,
            action=orm.action,
            outcome=AuditOutcome(orm.outcome),
            severity=AuditSeverity(orm.severity),
            entity_type=orm.entity_type,
            entity_id=orm.entity_id,
            actor_id=orm.actor_id,
            actor_type=orm.actor_type,
            request_id=orm.request_id,
            correlation_id=orm.correlation_id,
            source=orm.source,
            ip_address=orm.ip_address,
            before_state=json.loads(orm.before_state_json)
            if orm.before_state_json
            else None,
            after_state=json.loads(orm.after_state_json)
            if orm.after_state_json
            else None,
            metadata=json.loads(orm.metadata_json or "{}"),
            created_at=orm.created_at,
        )