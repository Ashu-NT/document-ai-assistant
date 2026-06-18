from src.application.services.audit import AuditService
from src.shared.audit import AuditContext, AuditOutcome, AuditSeverity


class FakeAuditRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, audit) -> None:
        self.saved.append(audit)

    def list_by_entity(self, entity_type: str, entity_id: str, limit: int = 50):
        return []


def test_audit_service_records_audit() -> None:
    repository = FakeAuditRepository()
    service = AuditService(repository)

    audit = service.record(
        action="document.deleted",
        context=AuditContext(
            actor_id="user_001",
            request_id="req_001",
            ip_address="127.0.0.1",
        ),
        entity_type="document",
        entity_id="doc_001",
        outcome=AuditOutcome.SUCCESS,
        severity=AuditSeverity.HIGH,
        before_state={"status": "active"},
        after_state={"status": "deleted"},
        metadata={"reason": "test"},
    )

    assert audit.action == "document.deleted"
    assert audit.actor_id == "user_001"
    assert audit.ip_address == "127.0.0.1"
    assert len(repository.saved) == 1