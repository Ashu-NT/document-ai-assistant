import pytest

from src.shared.audit import AuditContext, AuditOutcome
from src.shared.execution import ActionResult, tracked_action


class FakeAuditService:
    def __init__(self) -> None:
        self.records = []

    def record(self, **kwargs):
        self.records.append(kwargs)


class ExampleAuditService:
    def __init__(self) -> None:
        self.audit_service = FakeAuditService()

    @tracked_action(
        action="document.deleted",
        entity_type="document",
        activity=False,
        audit=True,
    )
    def delete_document(self, document_id: str, audit_context=None):
        return ActionResult(
            entity_type="document",
            entity_id=document_id,
            message="Document deleted.",
            payload={"document_id": document_id},
        )

    @tracked_action(
        action="document.delete_failed",
        entity_type="document",
        activity=False,
        audit=True,
    )
    def fail(self, audit_context=None):
        raise RuntimeError("delete failed")

    @tracked_action(
        action="question_generation.generated",
        entity_type="question",
        activity=False,
        audit=True,
    )
    def generate_questions(self, audit_context=None):
        return ["Question one?", "Question two?"]


def test_tracked_action_records_audit_success() -> None:
    service = ExampleAuditService()

    service.delete_document(
        "doc_001",
        audit_context=AuditContext(actor_id="user_001"),
    )

    assert len(service.audit_service.records) == 1

    record = service.audit_service.records[0]

    assert record["action"] == "document.deleted"
    assert record["entity_id"] == "doc_001"
    assert record["outcome"] == AuditOutcome.SUCCESS
    assert record["after_state"]["document_id"] == "doc_001"


def test_tracked_action_records_audit_failure() -> None:
    service = ExampleAuditService()

    with pytest.raises(RuntimeError):
        service.fail(audit_context=AuditContext(actor_id="user_001"))

    assert len(service.audit_service.records) == 1

    record = service.audit_service.records[0]

    assert record["action"] == "document.delete_failed"
    assert record["outcome"] == AuditOutcome.FAILURE
    assert record["metadata"]["error_type"] == "RuntimeError"


def test_tracked_action_records_audit_for_list_results() -> None:
    service = ExampleAuditService()

    service.generate_questions(
        audit_context=AuditContext(actor_id="user_001"),
    )

    assert len(service.audit_service.records) == 1

    record = service.audit_service.records[0]

    assert record["action"] == "question_generation.generated"
    assert record["entity_type"] == "question"
    assert record["outcome"] == AuditOutcome.SUCCESS
    assert record["after_state"]["result_count"] == 2
    assert record["after_state"]["result_type"] == "list"
    assert record["metadata"]["message"] is None
