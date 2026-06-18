from src.domain.audit import AuditRecord
from src.infrastructure.db.mappers.audit import AuditRecordMapper
from src.shared.audit import AuditOutcome, AuditSeverity


def test_audit_record_mapper_round_trip() -> None:
    audit = AuditRecord(
        action="document.deleted",
        outcome=AuditOutcome.SUCCESS,
        severity=AuditSeverity.HIGH,
        entity_type="document",
        entity_id="doc_001",
        actor_id="user_001",
        before_state={"status": "active"},
        after_state={"status": "deleted"},
        metadata={"reason": "test"},
    )

    orm = AuditRecordMapper.to_orm(audit)
    domain = AuditRecordMapper.to_domain(orm)

    assert domain.audit_id == audit.audit_id
    assert domain.action == audit.action
    assert domain.outcome == AuditOutcome.SUCCESS
    assert domain.severity == AuditSeverity.HIGH
    assert domain.before_state["status"] == "active"
    assert domain.after_state["status"] == "deleted"
    assert domain.metadata["reason"] == "test"