from src.domain.audit import AuditRecord
from src.shared.audit import AuditOutcome, AuditSeverity


def test_audit_repository_saves_and_lists_by_entity(db_uow) -> None:
    audit = AuditRecord(
        action="document.deleted",
        outcome=AuditOutcome.SUCCESS,
        severity=AuditSeverity.HIGH,
        entity_type="document",
        entity_id="doc_001",
        actor_id="user_001",
        metadata={"reason": "cleanup"},
    )

    db_uow.audit.save(audit)
    db_uow.commit()

    records = db_uow.audit.list_by_entity(
        entity_type="document",
        entity_id="doc_001",
    )

    assert len(records) == 1
    assert records[0].action == "document.deleted"
    assert records[0].severity == AuditSeverity.HIGH