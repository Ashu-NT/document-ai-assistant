from src.application.workflows.ingestion.ingestion_exceptions import (
    DeleteDocumentNotSupportedError,
)
from src.shared.activity import ActivityContext
from src.shared.audit import AuditContext
from src.shared.execution import tracked_action


class DeleteDocumentWorkflow:
    @tracked_action(
        action="document.delete.requested",
        entity_type="document",
        activity=True,
        audit=True,
        event=False,
    )
    def run(
        self,
        document_id: str,
        *,
        activity_context: ActivityContext | None = None,
        audit_context: AuditContext | None = None,
    ) -> None:
        raise DeleteDocumentNotSupportedError(
            "Document deletion is not implemented safely yet.",
            error_code="delete_not_supported",
            details={"document_id": document_id},
        )
